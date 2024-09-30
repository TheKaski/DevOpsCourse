FROM golang:1.19 AS builder

WORKDIR /usr/src/app

# For downloading dependencies similar to python requirements.txt
COPY go.mod ./
RUN go mod download

# Copy service 2 source code
COPY *.go ./

RUN go build -o service2 .

CMD ["./service2"]