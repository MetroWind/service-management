#![allow(non_snake_case)]

use std::io::prelude::*;
use std::io::BufReader;
use std::fs::File;
use std::net::TcpListener;
use std::collections::HashMap;
use std::process::{Command, Stdio};

use httparse;
use url;
use clap;
use regex;

mod error;
use crate::error::Error;

const TTL: u32 = 60;
const KEY_FILE: &str = "/var/run/named/session.key";

fn regexMatch<'a>(pattern: &str, text: &'a str) -> Result<Vec<Option<&'a str>>, Error>
{
    if let Some(caps) = regex::Regex::new(pattern)
        .map_err(|e| rterr!("Invalid regexp: '{}', {}", pattern, e))?
        .captures(text)
    {
        return Ok(caps.iter().map(|c| c.map(|cc| cc.as_str())).collect());
    }
    else
    {
        return Ok(Vec::new());
    }
}

fn stripTrailingNewline<'a>(s: &'a str) -> &'a str
{
    s.strip_suffix("\n").or(Some(s)).unwrap()
}

fn readDefaultKey() -> Result<String, Error>
{
    let mut reader = BufReader::new(File::open(KEY_FILE).map_err(
        |_| rterr!("Failed to open file"))?);
    let mut line = String::new();
    reader.read_line(&mut line).map_err(|_| rterr!("Failed to read file"))?;
    let key_name = regexMatch(r#"^key "(.+)" \{$"#,
                              stripTrailingNewline(&line))?.get(1)
        .ok_or_else(|| rterr!("Invalid 1st line of key file"))?
        .ok_or_else(|| rterr!("Invalid 1st line of key file"))?.to_owned();
    line.clear();
    reader.read_line(&mut line).map_err(|_| rterr!("Failed to read file"))?;
    let key_algo = regexMatch(r#"^\s*algorithm (.+);$"#,
                              stripTrailingNewline(&line))?.get(1)
        .ok_or_else(|| rterr!("Invalid 2nd line of key file: {}", line))?
        .ok_or_else(|| rterr!("Invalid 2nd line of key file: {}", line))?.to_owned();
    line.clear();
    reader.read_line(&mut line).map_err(|_| rterr!("Failed to read file"))?;
    let key = regexMatch(r#"^\s*secret "(.+)";$"#,
                         stripTrailingNewline(&line))?.get(1)
        .ok_or_else(|| rterr!("Invalid 3rd line of key file"))?
        .ok_or_else(|| rterr!("Invalid 3rd line of key file"))?.to_owned();

    Ok(format!("{}:{} {}", key_algo, key_name, key))
}

fn updateIP(domain: &str, ip: &str) -> Result<(), Error>
{
    let key = readDefaultKey()?;
    let update_str = format!("server localhost
zone {domain}
key {key}
update delete {domain}. A
update add {domain}. {ttl} A {ip}
send", domain=domain, key=key, ttl=TTL, ip=ip);
    let mut proc = Command::new("nsupdate")
        .stdin(Stdio::piped()).spawn()
        .map_err(|_| rterr!("Failed to launch nsupdate"))?;
    let mut stdin = proc.stdin.take()
        .ok_or_else(|| rterr!("Failed to take stdin"))?;
    std::thread::spawn(move || {
        stdin.write_all(update_str.as_bytes()).expect("Failed to write stdin")
    });
    if proc.wait().map_err(|_| rterr!("Failed to execute nsupdate"))?.success()
    {
        Ok(())
    }
    else
    {
        Err(rterr!("nsupdate failed"))
    }
}

fn updateTxt(domain: &str, name: &str, value: &str) -> Result<(), Error>
{
    let key = readDefaultKey()?;
    let update_str = format!("server localhost
zone {domain}
key {key}
update delete {name}. TXT
update add {name}. {ttl} TXT {value}
send", domain=domain, key=key, name=name, ttl=TTL, value=value);
    let mut proc = Command::new("nsupdate")
        .stdin(Stdio::piped()).spawn()
        .map_err(|_| rterr!("Failed to launch nsupdate"))?;
    let mut stdin = proc.stdin.take()
        .ok_or_else(|| rterr!("Failed to take stdin"))?;
    std::thread::spawn(move || {
        stdin.write_all(update_str.as_bytes()).expect("Failed to write stdin")
    });
    if proc.wait().map_err(|_| rterr!("Failed to execute nsupdate"))?.success()
    {
        Ok(())
    }
    else
    {
        Err(rterr!("nsupdate failed"))
    }
}

fn makeResponse(status: &str, body: &str) -> String
{
    format!("HTTP/1.1 {}\r\nContent-Length: {}\r\n\r\n{}", status, body.len(),
            body)
}

fn extractQueries(uri: &url::Url) -> HashMap<String, String>
{
    let mut queries: HashMap<String, String> = HashMap::new();
    for p in uri.query_pairs()
    {
        queries.insert(p.0.to_string(), p.1.to_string());
    }
    queries
}

fn handleRequest(buffer: &[u8]) -> Result<(), Error>
{
    let mut headers = [httparse::EMPTY_HEADER; 64];
    let mut req = httparse::Request::new(&mut headers);
    req.parse(&buffer).map_err(|_| rterr!("Failed to parse request"))?;

    if req.method != Some("GET")
    {
        return Err(rterr!("lalala"));
    }

    let full_path = format!("http://localhost:8080{}",
                            req.path.ok_or_else(|| rterr!("No path"))?);
    let uri = url::Url::parse(&full_path).map_err(
        |_| rterr!("Failed to parse URI: {}", full_path))?;
    match uri.path()
    {
        "/dns/update-ip" => {
            let queries = extractQueries(&uri);
            let domain: &str = queries.get("domain").ok_or_else(
                || rterr!("Domain needed"))?;
            let ip: &str = queries.get("ip").ok_or_else(
                || rterr!("IP needed"))?;
            updateIP(domain, ip)
        },
        "/dns/update-dns01-txt" => {
            let queries = extractQueries(&uri);
            let domain: &str = queries.get("domain").ok_or_else(
                || rterr!("Domain needed"))?;
            let value: &str = queries.get("value").ok_or_else(
                || rterr!("Value needed"))?;
            updateTxt(domain, &format!("_acme-challenge.{}", domain), value)
        },
        _ => Err(rterr!("Invalid path: {}", uri.path()))
    }

}

fn main()
{
    let matches = clap::App::new("DNS updater")
        .version("1.0")
        .author("Metro Wind <chris.corsair@gmail.com>")
        .about("Update DNS record on-demand")
        .arg(clap::Arg::with_name("address")
             .short("a")
             .long("address")
             .value_name("HOST")
             .help("Listen address")
             .takes_value(true))
        .arg(clap::Arg::with_name("port")
             .short("p")
             .long("port")
             .value_name("PORT")
             .help("Listen port")
             .takes_value(true))
        .get_matches();

    let address = matches.value_of("address").or(Some("localhost")).unwrap();
    let port = matches.value_of("port").or(Some("8080")).unwrap();

    let listener = TcpListener::bind(format!("{}:{}", address, port)).unwrap();

    for stream in listener.incoming()
    {
        let mut stream = stream.unwrap();
        let mut buffer = [0; 1024];
        stream.read(&mut buffer).unwrap();
        let res = match handleRequest(&buffer)
        {
            Ok(()) => makeResponse("200 OK", "ok"),
            Err(e) => {
                eprintln!("{}", e);
                makeResponse("500 Internal Server Error", &e.to_string())
            },
        };
        stream.write(res.as_bytes()).unwrap();
        stream.flush().unwrap();
    }
}
