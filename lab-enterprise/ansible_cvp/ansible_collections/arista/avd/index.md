<!--
  ~ Copyright (c) 2023-2024 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# Arista Validated Designs

<center><img src="media/avd-logo.png" alt="Arista AVD Overview" width="800"/></center>

Arista Validated Designs (AVD) is an extensible data model that defines Arista's Unified Cloud Network architecture as "code".

**[Documentation](https://avd.arista.com)**

**[Source Code](https://github.com/aristanetworks/avd)**

**[Examples](https://github.com/aristanetworks/avd/tree/devel/ansible_collections/arista/avd/examples)**

## Features

- **Flexibility with Open Data Models:** Extensible fabric-wide network models, simplifying configuration, delivering consistency, and reducing errors
- **Simplification through Multi-Domain Automation:** A framework that can automate the data center, campus or wide area network, enabled by a consistent EOS software image and management platform
- **Comprehensive Workflows:** Automating the full life cycle of network provisioning from config generation to pre and post-deployment validation, and self-documentation of the network

## Reference designs

- [L3LS VXLAN-EVPN, L2LS, and MPLS](roles/eos_designs/README.md)

## AVD Ansible Collection

[Arista Networks](https://www.arista.com/) supports Ansible for managing devices running Arista's **Extensible Operating System (EOS)** natively through it's **EOS API (eAPI)** or [**CloudVision Portal (CVP)**](https://www.arista.com/en/products/eos/eos-cloudvision). The collection includes a set of Ansible roles and modules to help kick-start your automation with Arista. The various roles and templates provided are designed to be customized and extended to your needs.

### Collection installation

Ansible galaxy hosts all stable versions of the `arista.avd` collection. Installation from ansible-galaxy is the most convenient approach for consuming `arista.avd` content. Please follow the collection installation [guide](docs/installation/collection-installation.md).

```shell
ansible-galaxy collection install arista.avd
```

## PyAVD

PyAVD is a python package providing some of the features from the arista.avd Ansible collection without requiring Ansible. PyAVD leverages the same logic as the Ansible collection, so the generated outputs should be exactly the same based on the same inputs.

PyAVD does not provide any inventory or variable management, so PyAVD cannot replace a full Ansible based solution by itself. PyAVD could serve as an element in larger framework.

```shell
pip3 install pyavd
```

## Examples

- [Getting started](docs/getting-started/intro-to-ansible-and-avd.md)
- [Arista NetDevOps GitHub repository](https://github.com/aristanetworks/netdevops-examples)

## Additional resources

- Ansible [EOS modules](https://docs.ansible.com/ansible/latest/collections/arista/eos/index.html) on Ansible documentation
- Ansible [CloudVision modules](https://cvp.avd.sh/en/stable/)
- [CloudVision Portal](https://www.arista.com/en/products/eos/eos-cloudvision)
- [Arista Design and Deployment Guides](https://www.arista.com/en/solutions/design-guides)

## Support

- AVD version 4.x releases with full support from Arista TAC. If your organization has the [A-Care subscription](https://www.arista.com/assets/data/pdf/AVD-A-Care-TAC-Support-Overview.pdf) please don't hesitate to contact TAC with any questions or issues.
- Community support is provided via [Github discussions board](https://github.com/aristanetworks/avd/discussions).

## Contributing

Contributing pull requests are gladly welcomed for this repository. If you are planning a big change, please start a discussion first to make sure we'll be able to merge it. Please see [contribution guide](docs/contribution/overview.md) for additional details.

You can also open an [issue](https://github.com/aristanetworks/avd/issues) to report any problems or submit enhancements.

## License

Copyright (c) 2019-2024 Arista Networks, Inc.

The project is published under [Apache 2.0 License](LICENSE)
