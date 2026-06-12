# gateway-infra
gateway-infra creation scripts

## Workflow

Two-step process. The issuer bootstrap is done once; domain sync is done whenever `domains.txt` changes.

### Step 1 — Bootstrap (once)

Creates the `gateway-infra` namespace, the Cloudflare API token Secret, and the cert-manager ACME Issuer. Re-run only if the token or email changes.

Interactive:
```
python3 issuer.py | kubectl apply -f -
```

Non-interactive:
```
python3 issuer.py --email=alex@example.com --api_token=<your_token> | kubectl apply -f -
```

Generate individual resources:
```
python3 issuer.py --resources=namespace
python3 issuer.py --email=alex@example.com --resources=issuer
python3 issuer.py --api_token=<your_token> --resources=secret
```

### Step 2 — Domain sync

Edit `domains.txt` (one domain per line), then run:
```
./gateway_sync.sh
```

This generates the cert-manager `Certificate` and `Gateway` listeners for every domain in `domains.txt` and applies them to the current kubectl context. No credentials required.

Dry-run (print manifest without applying):
```
./gateway_sync.sh --dry-run
```

Use a different domain list:
```
DOMAINS_FILE=other.txt ./gateway_sync.sh
```

Inspect certificates:
```
kubectl -n gateway-infra get certificate
```

### gateway.py (certificates + gateway only)

`gateway_sync.sh` calls this internally. Can also be used directly:
```
python3 gateway.py --domains=example.com,experiment.com
python3 gateway.py --domains_file=domains.txt --resources=certificates
python3 gateway.py --domains_file=domains.txt --resources=gateway
```

## Project

Interactive mode to generate all resources (default)
```
python3 default-project.py
Enter domain name: example.com
```

Generate all resources
```
python3 default-project.py --domain=example.com
```

Generate individual resources:
```
python3 default-project.py --domain=example.com --resources=namespace
python3 default-project.py --domain=example.com --resources=route
python3 default-project.py --domain=example.com --resources=service
python3 default-project.py --domain=example.com --resources=deployment
```
