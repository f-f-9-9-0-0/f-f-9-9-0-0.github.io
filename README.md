# Build locally

**NOTE:** the local config file is provided!

```bash
docker run --rm `
  --volume="$(pwd):/srv/jekyll:Z" `
  -it jekyll/builder:$JEKYLL_VERSION `
  jekyll build --config _config_local.yml
```

# Serve

**NOTE:** the local config file is provided!

```bash
docker run --rm `
  --volume="$(pwd):/srv/jekyll:Z" `
  --publish 127.0.0.1:4000:4000 `
  jekyll/jekyll:$JEKYLL_VERSION `
  jekyll serve --config _config_local.yml
```
