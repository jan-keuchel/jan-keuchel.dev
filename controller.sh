#/bin/bash

# This script was taken from Tomáš Sláma: https://slama.dev/
# (Then it was modified...)

serve() {
    echo "Starting Hugo development server..."
    if pgrep -f "hugo serve" > /dev/null; then
        echo "ERROR: Hugo server seems to be running already."
        return 1
    fi
    hugo serve --buildDrafts --buildFuture --disableFastRender
}

clean() {
    echo "Cleaning Hugo site..."
    rm -rf public/
}

build() {
    echo "Building Hugo site..."
    if pgrep -f "hugo serve" > /dev/null; then
        echo "ERROR: Hugo server seems to be running already."
        return 1
    fi
    hugo --gc --minify
}

check_localhost() {
    echo "Checking for localhost references..."
    if grep -r "localhost:1313" public/**/*.html > /dev/null 2>&1; then
        echo "ERROR: Found 'localhost' in HTML files, not uploading!"
        return 1
    else
        echo "     Check passed: No 'localhost' found."
        return 0
    fi
}

upload() {
    echo "Sourcing config file..."
    if [[ -f ./.deploy-config ]]; then
        source ./.deploy-config
    else
        echo "Error: .deploy-config file not found."
        exit 1
    fi

    echo -n "Are you sure you want to upload to VPS? (y/n): "
    read -r answer
    if [[ ! "$answer" =~ ^[Yy]$ ]]; then
        echo "Upload aborted."
        return 1
    fi

    echo "Uploading site to VPS..."

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
        echo "  serve   - Start Hugo dev server (drafts + future posts)"
        echo "  clean   - Remove generated files (public/)"
        echo "  build   - Build the site"
        echo "  upload  - Check for localhost and upload to VPS"
        echo "  all     - Build and upload"
        ;;
esac
