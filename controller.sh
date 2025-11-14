#/bin/bash

# This script was taken from Tomáš Sláma: https://slama.dev/

serve() {
    echo "Starting Jekyll development server..."
    if pgrep -f "ruby.*jekyll" > /dev/null; then
        echo "ERROR: Jekyll seems to be running already."
        return 1
    fi
    bundle exec jekyll serve --livereload --trace --config _config.yml
}

clean() {
    echo "Cleaning Jekyll site..."
    bundle exec jekyll clean --trace
}

build() {
    echo "Building Jekyll site..."
    if pgrep -f "ruby.*jekyll" > /dev/null; then
        echo "ERROR: Jekyll seems to be running already."
        return 1
    fi
    bundle exec jekyll build --trace
}

check_localhost() {
    echo "Checking for localhost references..."
    if grep -r "localhost:4000" _site/**/*.html > /dev/null 2>&1; then
        echo "ERROR: Found 'localhost' in HTML files, not uploading!"
        return 1
    else
        echo "     Check passed: No 'localhost' found."
        return 0
    fi
}

upload() {
    echo "Sourcing for config file..."
    if [[ -f ./.deploy-config ]]; then
        source ./.deploy-config
    else
        echo "Error: .deploy-config file not found."
        exit 1
    fi

    echo "Uploading site to VPS..."

    # Check for localhost references first
    if ! check_localhost; then
        return 1
    fi

    echo "Syncing files to VPS..."
    rsync -avz --zc=zstd --delete -e "ssh -i $SSH_KEY -p $PORT" $SOURCE_DIR $VPS_USER@$VPS_HOST:$VPS_PATH

    echo "Setting proper permissions..."
    ssh -i "$SSH_KEY" "$VPS_USER@$VPS_HOST -p $PORT" "chown -R www-data:www-data $VPS_PATH && chmod -R 755 $VPS_PATH"

    echo "Upload complete!"
}

case "$1" in
    serve)
        serve
        ;;
    clean)
        clean
        ;;
    build)
        build
        ;;
    upload)
        upload
        ;;
    all)
        build && upload
        ;;
    *)
        echo "Usage: ./controller.sh [serve|clean|build|upload|all]"
        echo ""
        echo "Commands:"
        echo "  serve   - Start development server with drafts and future posts"
        echo "  clean   - Clean generated files"
        echo "  build   - Build the site"
        echo "  upload  - Check for localhost and upload to VPS"
        echo "  all     - Build and upload"
        ;;
esac
