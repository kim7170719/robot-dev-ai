# M14 LAN read-only presentation

M14 normally binds to `127.0.0.1:8000` and is for the local Ubuntu operator.
For a demonstration on a controlled internal network, use the explicit
`lan-readonly` mode. It serves the static GUI plus GET/HEAD API evidence only;
every POST API returns `403`, including requirement parsing, template/workspace
generation, restricted build, Full Run, and fixed navigation validation.

This mode is a presentation surface, not a remote robot-control surface. It
does not make a physical robot, Jetson, motor, or Nav2 control API available.

## Preconditions

- Use only a controlled LAN. Do not configure router port forwarding, a public
  DNS record, or an Internet-facing security-group rule for this service.
- Reserve a stable host IP or DNS name for the Ubuntu host.
- Keep ROS, Isaac Sim, and hardware-control processes on Ubuntu. Windows is a
  viewer, Git, and documentation host only.
- Prefer the authenticated reverse-proxy setup below. Direct port 8000 access
  has no application login and is appropriate only for a tightly trusted,
  firewalled demonstration network.

## Recommended: authenticated HTTPS reverse proxy

Keep uvicorn on loopback and enable application-level read-only mode:

```bash
cd ~/dev/robot-dev-ai
ROBOT_DEV_AI_MODE=lan-readonly \
ROBOT_DEV_AI_LAN_BIND=127.0.0.1 \
bash scripts/run_m14_demo.sh
```

Configure the organisation's existing reverse proxy to listen only on its LAN
interface, require authentication, and proxy to `127.0.0.1:8000`. An Nginx
example follows; replace `192.168.10.20`, the certificate paths, and the name
before enabling it.

```nginx
server {
    listen 192.168.10.20:443 ssl;
    server_name robot-dev-ai.lab.internal;

    ssl_certificate     /etc/ssl/certs/robot-dev-ai.crt;
    ssl_certificate_key /etc/ssl/private/robot-dev-ai.key;

    auth_basic "Robot Dev AI internal demonstration";
    auth_basic_user_file /etc/nginx/.htpasswd-robot-dev-ai;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_read_timeout 75s;
    }
}
```

Create the password file with a unique, non-shared account and store the
certificate/private key using the lab's normal secret-management procedure.
Do not commit either file. Restrict firewall access to the intended LAN subnet,
for example (replace the subnet):

```bash
sudo ufw allow from 192.168.10.0/24 to any port 443 proto tcp
```

After Nginx configuration validation and reload, users browse:

```text
https://robot-dev-ai.lab.internal/
```

The certificate and reverse proxy are environment-owned deployment settings;
they are intentionally not installed or changed by this repository.

## Direct trusted-LAN demonstration (temporary)

If an authenticated proxy is unavailable for a short, supervised session, bind
uvicorn to the host's explicit LAN address—not `0.0.0.0`—and constrain the
firewall to the demonstration subnet:

```bash
cd ~/dev/robot-dev-ai
ROBOT_DEV_AI_MODE=lan-readonly \
ROBOT_DEV_AI_LAN_BIND=192.168.10.20 \
ROBOT_DEV_AI_PORT=8000 \
bash scripts/run_m14_demo.sh

sudo ufw allow from 192.168.10.0/24 to any port 8000 proto tcp
```

Users then open `http://192.168.10.20:8000/`. End the process and remove the
temporary firewall rule when the demonstration is over. This direct mode has
no HTTPS or login, so it must not be used on shared, guest, or untrusted LANs.

## Verification

From an allowed viewer machine, confirm that `/` and the Dashboard load and
that camera/runtime evidence is readable when its Ubuntu ROS source exists.
Then confirm a protected API is refused:

```bash
curl -i -X POST http://192.168.10.20:8000/api/v1/mvp/full-run
```

Expected result: `HTTP/1.1 403 Forbidden` and JSON detail
`M14 is running in read-only mode.` A `200`, `422`, or a generated workspace
means the service is not in the intended mode; stop it and check the launch
environment before sharing the URL.

## Rollback

Stop `scripts/run_m14_demo.sh`, remove any temporary UFW rule, and disable the
reverse-proxy site if one was enabled. Restart without `ROBOT_DEV_AI_MODE` to
return to local-only `127.0.0.1:8000` behavior.
