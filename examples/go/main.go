package main
import (
  "fmt"
  "os/exec"
)
func main() {
  out, err := exec.Command("skillbridge", "discover", "../manifests").CombinedOutput()
  if err != nil { panic(err) }
  fmt.Println(string(out))
}
