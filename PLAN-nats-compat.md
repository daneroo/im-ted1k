# PLAN: ted1k capture — NATS client compatibility

Tracker: https://github.com/daneroo/im-qcic/issues/313 (checkbox "ted1k capture")
Branch: `nats-compat-313`

## Question

Does the capture's NATS publishing (`go/ted1k/nats.go`, nats.go v1.27.1, plain
publish of JSON to `im.qcic.heartbeat`, no JetStream) work against the latest
NATS release (`nats:2.15.0`, released 2026-09-17)?

The current code already works in production against the pinned server
(`synadia/nats-server:nightly-20220224`, v2.7.3-beta.3). If it also works
against the latest release, then one build already covers both and #313 is
answered with no code change. Only if it fails do we look at `nats:2.7.2` and
at the smallest code change.

## Constraints

- Don't touch the production USB device, host darwin, or the live NATS server.
  All testing is local (Docker on this Mac).
- Don't use the root `docker-compose.yml`: it is the production stack
  (privileged `/dev` mount, `./data/mysql`, other services, `restart: unless-stopped`).
- Don't change toolchain or dependencies: build with the production
  `go/Dockerfile` (`golang:1.20`, set 2023-07-01 in `1047510`). No local
  `go get` / `go mod tidy`.
- Ask before committing. Ask before posting to #313.

## Approach: unchanged code, local server

No code change. The capture's startup is the test:

1. connect to NATS (`nats.ts.imetrical.com:4222`, hardcoded)
2. publish `"Start"` to `im.qcic.heartbeat` (`cmd/capture/main.go:34`)
3. open MySQL: fails (no `teddb` host), sleeps 5s, exits (`ted1k/db.go:22-24`)

The USB device is never reached. The 5s sleep lets nats.go flush the message.

Setup, on a throwaway Docker network, cleaned up afterwards:

- NATS server under test
- nats-box (official image with the `nats` CLI) running `nats sub im.qcic.heartbeat`
- capture image built from `go/Dockerfile`, run with
  `--add-host nats.ts.imetrical.com:<server IP>` so the hardcoded hostname
  resolves to the local server inside that container only

Pass: the subscriber receives the `"Start"` JSON, and the server log shows
client `capture.ted1k` connecting with no warnings.

Covered: connect, handshake, publish of JSON.
Not covered: per-reading `Write(Entry)` (same connection and `Publish` call)
and reconnect.

Images: `nats:2.7.2`, `nats:2.15.0`, `golang:1.20`, `nats-box` have arm64 builds.
The pinned `synadia/nats-server:nightly-20220224` is amd64 only: run it with
`--platform linux/amd64` (emulated).

## Plan

- [x] Read #313 and the capture code
- [x] Create branch `nats-compat-313` and this plan
- [x] Script the setup above so it can be rerun per server image:
      `go/nats-compat/run.sh <image> [platform]` (only the 3 containers, no MySQL, no `/dev`)
- [x] Control: run against the pinned server (should pass, like production): PASS
- [x] Run against `nats:2.15.0`: PASS
- [x] ~~Only if (latest) fails~~ (latest passed; 2.7.2 run anyway: PASS): run against `nats:2.7.2`, list options for the
      smallest change (e.g. a nats.go bump), decide with the user
- [ ] Draft the #313 checkbox line and comment, review with the user, then post

## Results

| Server                        | Connect | "Start" received | Server log notes |
| ----------------------------- | ------- | ---------------- | ---------------- |
| pinned nightly-20220224 (ctl) | OK      | yes              | none for client (1) |
| nats:2.15.0                   | OK      | yes              | none             |
| nats:2.7.2 (tried/reverted 2022-03-01) | OK | yes          | none             |

All three servers log the same exchange for client `v1.27.1:go:capture.ted1k`:
CONNECT (protocol 1, headers, no_responders) → PING/PONG →
`PUB im.qcic.heartbeat 80` with the `"Start"` JSON → server PING/PONG →
"Client Closed" when the capture exits. The nats-box subscriber received the
message on all three.

(1) The pinned server logs `[WRN] Cluster name was dynamically generated`: that
is about the image's own cluster config, not the client.

## Log

- 2026-09-28: Plan agreed. Branch created.
- 2026-09-28: Go toolchain pinned by `go/Dockerfile` (`golang:1.20`); build there only.
- 2026-09-28: Switched to a no-code-change test: unchanged capture image,
  `--add-host` to a local NATS server, nats-box subscriber. Latest server is the
  main question; pinned run is a control; `nats:2.7.2` only if latest fails.
- 2026-09-28: Wrote `go/nats-compat/run.sh`. Control (pinned, amd64 emulated)
  PASS. `nats:2.15.0` PASS. `nats:2.7.2` skipped. No code change needed.
- 2026-09-28: Ran `nats:2.7.2` anyway (the release tried and reverted on
  2022-03-01): PASS. The capture is not a likely cause of that revert.
- 2026-09-28: Verified on darwin (read-only, run by user): running container
  `im-ted1k-capture-1` has nats.go v1.27.1 compiled in; image created
  2023-07-01T15:35 (the `1047510` build). Today's tests cover what is deployed:
  the server can be upgraded to latest without rebuilding the capture.
- 2026-09-28: Outcome: no code change. `master` untouched. Branch
  `nats-compat-313` pushed (not merged) with this plan and
  `go/nats-compat/run.sh`, kept for now. Recorded in #313.
  Out of scope, for later: startup resilience (exit if NATS unreachable,
  restart loop), reconnect testing.
