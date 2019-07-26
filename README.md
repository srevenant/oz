# AWS phonetic -> Oz

Oz is tooling to ease scriptable AWS, beyond boto, and simpler than terraform/salt and other
conventional stack automation tools (oz doesn't require the heavy overhead required by these,
just python, which is useful for some lean cases).

It is a _Work in Progress_, as I consolidate from a variety of hodge-podge utilities and clean them up.

The first tool:

  *oz-aws-bootstrap* - create an securely designed VPC in Amazon (available in a container)
  *rds-snap-clone* - automate a snapshot->clone of an EC2 instance

# oz-aws-bootstrap

Create VPC and all its bits, in a PCI/SOC/SOX/ISO manner, with zone separation and the works.

It also auto-calculate subnets and sets up things so they can be properly routed with CIDR blocks.

See also bootstrap-example.yml

Edit:

    data/bootstrap-example.yml, put in files assuming it imports data/ into /data (such as ssh key)

Run in docker:

    cd bootstrap
    docker-compose build
    docker-compose run cli oz-aws-bootstrap data/yourfile.yml

    # or for a shell:
    docker-compose run cli /bin/sh
