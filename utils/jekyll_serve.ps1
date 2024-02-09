$CONTAINER_NAME = "JEKYLL-SERVE__$((Split-Path -Path (Join-Path (Get-Location) '..') -Leaf) -replace '\.', '_')"
$VOLUME         = "$(Get-Location)/../:/srv/jekyll:Z"
$PUBLISH        = "127.0.0.1:4000:4000"

Clear-Host

docker run --rm `
  --name=$CONTAINER_NAME `
  --volume=$VOLUME `
  --publish $PUBLISH `
  jekyll/jekyll `
  jekyll serve --config _config.yml,_config_development.yml
