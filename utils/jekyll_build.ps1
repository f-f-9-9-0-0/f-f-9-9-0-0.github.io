$CONTAINER_NAME = "JEKYLL-BUILD__$((Split-Path -Path (Join-Path (Get-Location) '..') -Leaf) -replace '\.', '_')"
$VOLUME         = "$(Get-Location)/../:/srv/jekyll:Z"

Clear-Host

docker run --rm `
  --name=$CONTAINER_NAME `
  --volume=$VOLUME `
  -it jekyll/builder `
  jekyll build --config _config.yml,_config_development.yml
