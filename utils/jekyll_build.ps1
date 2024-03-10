$CONTAINER_NAME = "JEKYLL-BUILD__$((Split-Path -Path (Join-Path $PSScriptRoot '..') -Leaf) -replace '\.', '_')"
$VOLUME         = "$($PSScriptRoot)/../:/srv/jekyll:Z"

Clear-Host

docker run --rm `
  --name=$CONTAINER_NAME `
  --volume=$VOLUME `
  -it jekyll/builder `
  jekyll build --config _config.yml,_config_development.yml
