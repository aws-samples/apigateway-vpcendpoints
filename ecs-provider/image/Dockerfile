# Start from Alpine Linux image with the latest version of Golang
# Naming build stage as builder
FROM golang:alpine as builder


# Install Git for go get
RUN set -eux; \
    apk add --no-cache git

RUN mkdir /app

# Add files to image
COPY . /app

WORKDIR /app

ENV GO111MODULE=auto

# Fetch Golang Dependency and Build Binary
RUN go get "github.com/sirupsen/logrus"
RUN go build -o server .

# Start from a raw Alpine Linux image
FROM alpine:latest

# Copy binary from builder stage into image
COPY --from=builder /app/server .

# Execute binary when docker container starts
CMD /server

# Expose port 8080 to be connected from outside
EXPOSE 8080