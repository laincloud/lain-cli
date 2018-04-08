package main

import (
	"context"
	"net/http"
	"os"
	"os/signal"
	"syscall"
)

func main() {
	// Capture SIGTERM
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGTERM)

	mux := http.NewServeMux()

	// Health check endpoint
	mux.HandleFunc("/ping", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("OK"))
	})

	// Business logic endpoint
	mux.HandleFunc("/hello", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("Hello, world.\n"))
	})

	server := &http.Server{
		Addr:    ":8080",
		Handler: mux,
	}

	go server.ListenAndServe()

	<-quit
	server.Shutdown(context.Background())
	// Any other clean up actions...
}
