#!/usr/bin/env ruby
# Check the rendered site's shared layout, navigation, and article anchors.
require 'nokogiri'
require 'pathname'
require 'uri'

root = Pathname.new(ARGV.fetch(0, '_site')).expand_path
pages = root.glob('**/*.html')
raise 'No generated pages found' if pages.empty?

pages.each do |path|
  html = path.read
  page = Nokogiri::HTML5(html, max_errors: 100)
  name = path.relative_path_from(root).to_s
  raise "#{name}: expected one main landmark" unless page.css('main').size == 1
  raise "#{name}: expected one page heading" unless page.css('h1').size == 1
  raise "#{name}: missing skip target" unless page.at_css('a.skip-link')['href'] == '#main-content' && page.at_css('main#main-content')
  raise "#{name}: external icon loader remains" if html.match?(/FontAwesomeKitConfig|kit\.fontawesome\.com/)
  raise "#{name}: extra closing wrapper" if page.errors.any? { |error| error.message.include?("End tag 'div' isn't allowed here") }
  nav = page.at_css('nav[aria-label="Main navigation"]')
  raise "#{name}: missing persistent navigation" unless nav && nav.css('a').map(&:text).include?('Home')
  current = nav.css('[aria-current="page"]')
  expected = if page.at_css('main.post')
    'Blog'
  else
    { 'index.html' => 'Home', 'blog/index.html' => 'Blog', 'projects/index.html' => 'Projects', 'about/index.html' => 'About', 'tags/index.html' => 'Blog' }[name]
  end
  raise "#{name}: wrong active section" if expected && (current.size != 1 || current.first.text != expected)
  raise "#{name}: multiple active sections" if current.size > 1
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
puts "Design checks passed: #{pages.size} pages; landmarks, headings, navigation, contents anchors and shared assets"
