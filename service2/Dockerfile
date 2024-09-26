FROM golang:1.19 AS builder

WORKDIR /usr/src/app

# For downloading dependencies similar to python requirements.txt
COPY go.mod ./

RUN go mod download

# Copy service 2 source code
COPY *.go ./

RUN CGO_ENABLED=0 GOOS=linux go build -o /app/service2

FROM scratch

COPY --from=builder /app/service2 /service2

CMD ["/service2"]