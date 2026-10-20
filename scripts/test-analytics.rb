require 'liquid'
require 'json'
require 'cgi'

module AnalyticsFilters
  def jsonify(value)
    JSON.generate(value)
  end
  def escape(value)
    CGI.escapeHTML(value.to_s)
  end
end
Liquid::Template.register_filter(AnalyticsFilters)

class AnalyticsTemplateTest
  def assert_equal(expected, actual)
    raise "Expected #{expected.inspect}, got #{actual.inspect}" unless expected == actual
  end

  def assert_includes(value, expected)
    raise "Missing #{expected.inspect}" unless value.include?(expected)
  end

  def refute_includes(value, forbidden)
    raise "Unexpected #{forbidden.inspect}" if value.include?(forbidden)
  end
  def render(token, environment = 'production', enabled = true)
    source = File.read(ENV.fetch('ANALYTICS_TEMPLATE'))
    Liquid::Template.parse(source, error_mode: :strict).render!(
      'site' => {'data' => {'cloudflare_analytics' => {'token' => token}}},
      'jekyll' => {'environment' => environment},
      'page' => {'analytics' => enabled}
    )
  end

  def test_disabled_states_emit_no_script
    [nil, '', '  '].each { |token| refute_includes render(token), '<script' }
    refute_includes render('a' * 32, 'development'), '<script'
    refute_includes render('a' * 32, 'production', false), '<script'
  end

  def test_production_token_emits_one_valid_beacon
    html = render('a' * 32)
    assert_equal 1, html.scan('<script').length
    assert_includes html, 'defer src="https://static.cloudflareinsights.com/beacon.min.js"'
    config = CGI.unescapeHTML(html.match(/data-cf-beacon='([^']+)'/)[1])
    assert_equal({'token' => 'a' * 32}, JSON.parse(config))
  end
end

test = AnalyticsTemplateTest.new
test.test_disabled_states_emit_no_script
test.test_production_token_emits_one_valid_beacon
puts "Analytics templates: production, missing token, development and opt-out passed"
