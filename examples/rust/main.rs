use std::process::Command;
fn main() {
    let out = Command::new("skillbridge").args(["discover", "../manifests"]).output().expect("Install skillbridge CLI");
    assert!(out.status.success(), "{}", String::from_utf8_lossy(&out.stderr));
    println!("{}", String::from_utf8_lossy(&out.stdout));
}
