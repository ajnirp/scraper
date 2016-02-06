building: `cargo build --debug` OR `cargo build --release`

running: `./target/release/scraper -f filename.txt` OR `./target/release/scraper -u http://name.tistory.com/100`. Add a `-s` flag to download in single-threaded mode.

This program fetches a list of image links from the image source of a website, matched against a static regex. Then it creates 4 threads and divides download tasks amongst them.

TODO: multiplexed connections over HTTP/2