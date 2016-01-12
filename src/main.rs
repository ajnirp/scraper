extern crate argparse;
extern crate hyper;
extern crate regex;

use argparse::{ArgumentParser, Print, Store, StoreTrue};
use hyper::Client;
use hyper::header::Connection;
use hyper::header::ContentType;
use regex::Regex;
use std::collections::BTreeSet;
use std::fs::File;
use std::io::{Read, Write};
use std::sync::Arc;
use std::thread;

// Download the image located at 'url', and save the downloaded image
// to a file named "$(prefix)(idx).jpg"
fn download_image(url: &str, idx: u32, prefix: &str, client: &Client) {
    let mut image = Vec::<u8>::new();
    let idx = idx + 1;
    let mut res = client.get(url)
                    .header(ContentType::jpeg())
                    .send()
                    .unwrap();
    res.read_to_end(&mut image).unwrap();
    let filename = prefix.to_string() + &(idx.to_string()) + ".jpg";
    File::create(&filename).and_then(|mut file| {
        file.write_all(&image)
    }).unwrap();
    // println!("wrote {}", filename);
}

// Parse the URL. If it is a tistory URL, return
// the string <name>-<page#>-, else ""
fn prefix_from_url(url: &str) -> String {
    let re = Regex::new(r"https?://(\w+)\.tistory\.com/([0-9]+)").unwrap();
    re.captures(url).map_or("".to_owned(), |cap| {
        let tistory_name = cap.at(1).unwrap().to_owned();
        let page_num = cap.at(2).unwrap().to_owned();
        tistory_name + "-" + &page_num + "-"
    })
}

// Download a list of images, one at a time
fn download_single_threaded(urls: Vec<String>, prefix: &str) {
    let client = Client::new();
    let mut idx = 1;
    for url in urls {
        download_image(&url, idx, prefix, &client);
        idx += 1;
    }
}

fn main() {
    let mut url = "".to_owned();
    let mut file = "".to_owned();
    let mut single_threaded = false;

    {
        let mut parser = ArgumentParser::new();
        parser.set_description("image scraper");
        parser.add_option(&["-v", "--version"],
                          Print(env!("CARGO_PKG_VERSION").to_string()),
                          "Show version");
        parser.refer(&mut url)
              .add_option(&["-u", "--url"],
                          Store,
                          "URL to download from");
        parser.refer(&mut file)
              .add_option(&["-f", "--file"],
                          Store,
                          "File containing image links");
        parser.refer(&mut single_threaded)
              .add_option(&["-s", "--single-threaded"],
                StoreTrue,
                "Use single-threaded downloading. By default multiple threads are used.");
        parser.parse_args_or_exit();
    }

    // exactly one of -u and -f should be used
    if url.is_empty() == file.is_empty() {
        writeln!(std::io::stderr(),
                 "usage: scraper -u <url> OR scraper -f <file>").unwrap();
        std::process::exit(1);
    }

    let filename_prefix = prefix_from_url(&url);

    let urls = if file.is_empty() {
        let re_downscaled = Regex::new(r"http://cfile\d\d?\.uf\.tistory\.com/image/(\w|\d)+").unwrap();
        let re_original = Regex::new(r"http://cfile\d\d?\.uf\.tistory\.com/original/(\w|\d)+").unwrap();

        let client = Client::new();
        let mut res = client.get(&url)
                            .header(Connection::close())
                            .send()
                            .unwrap();
        let mut body = String::new();
        res.read_to_string(&mut body).unwrap();

        let mut urls = re_original.captures_iter(&body).map(|cap|
            cap.at(0).unwrap().to_owned()).collect::<BTreeSet<_>>();

        for cap in re_downscaled.captures_iter(&body) {
            let url = cap.at(0).unwrap().to_owned();
            url.replace("/image/", "/original/");
            if !urls.contains(&url) {
                urls.insert(url);
            }
        }

        urls.iter()
            .map(|u| u.to_owned())
            .collect::<Vec<_>>()
    } else {
        let mut contents = String::new();
        let _ = File::open(&file).and_then(|mut f| {
            f.read_to_string(&mut contents)
        });
        contents.lines()
                .map(|u| u.to_owned())
                .collect::<Vec<_>>()
    };

    // Single-threaded download
    if single_threaded {
        download_single_threaded(urls, &filename_prefix);
        return;
    }

    // Multi-threaded download
    let urls = Arc::new(urls);
    const NTHREADS: usize = 4;

    let mut children = vec![];

    for i in 0..NTHREADS {
        let urls = urls.clone();
        let prefix = filename_prefix.clone();
        children.push(thread::spawn(move || {
            let client = Client::new();
            let mut j = i;
            while j < urls.len() {
                let ref url = urls[j];
                println!("thread {} downloaded {} {}", i, j, url);
                download_image(&url, j as u32, &prefix, &client);
                j += NTHREADS;
            }
        }));
    }

    for child in children {
        let _ = child.join();
    }
}