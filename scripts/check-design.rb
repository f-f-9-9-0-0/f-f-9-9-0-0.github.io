#!/usr/bin/env ruby
# Check the rendered site's shared layout, navigation, and article anchors.
require 'nokogiri'
require 'pathname'
require 'uri'
require 'json'

root = Pathname.new(ARGV.fetch(0, '_site')).expand_path
pages = root.glob('**/*.html')
raise 'No generated pages found' if pages.empty?

home = Nokogiri::HTML5(root.join('index.html').read)
origin = home.at_css('link[rel="canonical"]')['href'].delete_suffix('/')
descriptions = {}
pages.each do |path|
  html = path.read
  page = Nokogiri::HTML5(html, max_errors: 100)
  name = path.relative_path_from(root).to_s
  raise "#{name}: expected one main landmark" unless page.css('main').size == 1
  raise "#{name}: expected one page heading" unless page.css('h1').size == 1
  raise "#{name}: missing skip target" unless page.at_css('a.skip-link')['href'] == '#main-content' && page.at_css('main#main-content')
  raise "#{name}: external icon loader remains" if html.match?(/FontAwesomeKitConfig|kit\.fontawesome\.com/)
  raise "#{name}: extra closing wrapper" if page.errors.any? { |error| error.message.include?("End tag 'div' isn't allowed here") }
  ids = page.css('[id]').map { |element| element['id'] }
  raise "#{name}: duplicate element IDs" unless ids.size == ids.uniq.size
  raise "#{name}: missing document title" if page.at_css('title')&.text.to_s.strip.empty?
  description = page.at_css('meta[name="description"]')&.[]('content').to_s.strip
  raise "#{name}: missing description" if description.empty?
  descriptions[name] = description
  canonical_path = '/' + name.delete_suffix('index.html')
  raise "#{name}: canonical mismatch" unless page.css('link[rel="canonical"]').map { |element| element['href'] } == [origin + canonical_path]
  page.css('script[type="application/ld+json"]').each { |script| JSON.parse(script.text) }
  page.css('main.post pre').each do |code|
    raise "#{name}: code block is not keyboard accessible" unless code['tabindex'] == '0' && code['role'] == 'region' && !code['aria-label'].to_s.empty?
  end
  page.css('.share a').each do |link|
    raise "#{name}: share link requires JavaScript" unless link['href'].to_s.start_with?('https://') && !link['onclick']
  end
  nav = page.at_css('nav[aria-label="Main navigation"]')
  raise "#{name}: missing persistent navigation" unless nav && nav.css('a').map(&:text).include?('Home')
  current = nav.css('[aria-current]')
  expected = if page.at_css('main.post')
    'Blog'
  else
    { 'index.html' => 'Home', 'blog/index.html' => 'Blog', 'projects/index.html' => 'Projects', 'about/index.html' => 'About', 'tags/index.html' => 'Blog' }[name]
  end
  raise "#{name}: wrong active section" if expected && (current.size != 1 || current.first.text != expected)
  raise "#{name}: multiple active sections" if current.size > 1
  if current.size == 1
    expected_current = current.first['href'] == canonical_path ? 'page' : 'true'
    raise "#{name}: active section claims to be the current page" unless current.first['aria-current'] == expected_current
  end
  if page.at_css('html')['lang'] == 'hu'
    %w[.site-header .footer-main .skip-link].each do |selector|
      raise "#{name}: English interface language is undeclared" unless page.at_css(selector)['lang'] == 'en'
    end
  end
  page.css('.post-toc a').each do |link|
    id = link['href'].delete_prefix('#')
    raise "#{name}: broken contents link #{id}" unless page.xpath('//*[@id=$id]', nil, id: id).size == 1
    raise "#{name}: empty contents label" if link.text.strip.empty?
  end
  page.css('.site-header a, .footer-main a, .home-writing a, link[rel="stylesheet"]').each do |link|
    href = link['href']
    next unless href&.start_with?('/') && !href.start_with?('//')
    target = root.join(URI::DEFAULT_PARSER.unescape(href.split('#').first).delete_prefix('/'))
    target = target.join('index.html') if target.directory?
    raise "#{name}: missing local target #{href}" unless target.file?
  end
end
landing_pages = %w[index.html about/index.html blog/index.html projects/index.html tags/index.html]
landing_descriptions = descriptions.values_at(*landing_pages)
raise 'Landing pages need distinct descriptions' unless landing_descriptions.uniq.size == landing_pages.size
puts "Design checks passed: #{pages.size} pages; landmarks, headings, navigation, contents anchors and shared assets"
