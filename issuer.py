from string import Template
import argparse

separator = "---"

namespace_t = """
apiVersion: v1
kind: Namespace
metadata:
  labels:
    kubernetes.io/metadata.name: gateway-infra
    project: gateway-infra
  name: gateway-infra
"""

secret_t = """
apiVersion: v1
kind: Secret
metadata:
  name: cloudflare-api-token
  namespace: gateway-infra
type: Opaque
stringData:
  api-token: ${api_token}
"""

issuer_t = """
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: acme-cert-issuer
  namespace: gateway-infra
spec:
  acme:
    # The ACME server URL
    server: https://acme-v02.api.letsencrypt.org/directory
    # Email address used for ACME registration
    email: ${email}
    # Name of a secret used to store the ACME account private key
    privateKeySecretRef:
      name: acme-cert-issuer-pk
    solvers:
    - dns01:
        cloudflare:
          apiTokenSecretRef:
            name: cloudflare-api-token
            key: api-token
"""


def format(tmpl, **kwargs):
    return Template(tmpl).safe_substitute(kwargs).strip('\n')


def gen_namespace(data):
    yield namespace_t.strip('\n')


def gen_secret(data):
    yield format(secret_t, api_token=data["api_token"])


def gen_issuer(data):
    yield format(issuer_t, email=data["email"])


resource_map = {
    "namespace": gen_namespace,
    "secret": gen_secret,
    "issuer": gen_issuer
}


def do_generate(resources, data):
    first = True
    for resource in resources:

        if resource not in resource_map:
            raise Exception(f"unknown resource '{resource}'")

        generator = resource_map[resource]

        for value in generator(data):
            if not first:
                print(separator)
            print(value)
            first = False


def parse_tokens(input_str):
    return [x.strip() for x in input_str.split(',')]


def generate(args):

    data = {}

    resources = parse_tokens(args.resources)

    if "issuer" in resources:
        email = args.email
        if email == None:
            email = input("Enter email for ACME account: ")
        data["email"] = email

    if "secret" in resources:
        api_token = args.api_token
        if api_token == None:
            api_token = input("Enter API-TOKEN of Cloudflare account: ")
        data["api_token"] = api_token

    outputFile = args.o
    if outputFile != None:
        import sys
        with open(outputFile, 'w') as sys.stdout:
            do_generate(resources, data)
    else:
        do_generate(resources, data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Issuer',
                    description='Gateway-infra issuer generator',
                    epilog='Copyright (C) Karagatan, LLC.')
    parser.add_argument("--resources", type=str, default='namespace,secret,issuer', help='generate type of resource')
    parser.add_argument("--email", type=str, help='email for ACME account')
    parser.add_argument("--api_token", type=str, help='API-TOKEN from Cloudflare account')
    parser.add_argument("-o", type=str, help='output file name')
    args = parser.parse_args()
    generate(args)
