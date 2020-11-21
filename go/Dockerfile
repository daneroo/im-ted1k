FROM golang:1.15 as build

WORKDIR $GOPATH/src/github.com/daneroo/im-ted1k/go

# Let's cache modules retrieval - those don't change so often
COPY go.mod .
COPY go.sum .
RUN go mod download

COPY . .

RUN go version

RUN go install ./...

# Base images: scratch 2.2MB alpine:6.3MB distroless:18MB ubuntu:19.04:79MB
# using ubuntu:20.04 (?because of glibc6 dependancy)
# FROM gcr.io/distroless/base
# FROM alpine
FROM ubuntu:20.04
COPY --from=build /go/bin/capture /

CMD ["/capture"]