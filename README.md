# Ansible WireGuard

This Ansible role allows you to install a single or dual stack (IPv4 and IPv6) Wireguard VPN "server".
You can also add an arbitrary number of peers, as long as the public key is provided. 
This role can also create the config files for the connecting peers, when the public and private keys are provided.

## Requirements

This role does not have any requirements.

## Coverage

Any combination of the following is tested:

- Operating System
  - Ubuntu 20.04 LTS
  - Debian 10
- Ansible
  - 2.9.x
  - 3.x
  - 4.x 
- Python
  - 3.8
  - 3.9

## Install Role

To install this role into your `roles` folder just clone, download or run: 

```bash
ansible-galaxy install --roles-path ./roles git+https://github.com/akutschi/ansible_wireguard.git,v0.1.0
```

## Role Variables

Here you can see all settable variables for this role. The defaults can be found in `default/main.yml`. 
The defaults are chosen in a reasonable way, so that no additional parameters must be set to the role.

| Variable | Default | Description
|-|-|-|
| wireguard_enable_ipv4 | `true` | _Enable_ IPv4 stack in WireGuard. |
| wireguard_enable_ipv6 | `true` | _Enable_ IPv6 stack in WireGuard. |
| wireguard_client_files_remote | `true` | Store client configuration files remotely. If set `false` the client files will be stored locally. |
| wireguard_interface | `wg0` | Defines the name of the default interface for Wireguard
| public_interface | `{{ ansible_default_ipv4.interface }}` | Sets the default public interface. By default this setting comes from the collected facts. |
| wireguard_network_ipv4 | `192.168.42` | The first 24 bits of the IPv4 network. |
wireguard_network_ipv6 | `d91:34d4:2692:9dfb:` | The first 64 bit of the IPv6 network. If you do not have your own IPv6 range, you can generate [here](https://simpledns.plus/private-ipv6) a random private IPv6 range. The default one is such a random private IPv6 range. |
| wireguard_port | `51820` | The Wireguard port. The default one is the default one.
| dns_ipv4_1 | `1.1.1.1` | Cloudflare [DNS server](https://1.1.1.1/). See also [Wikipedia](https://en.wikipedia.org/wiki/1.1.1.1)
| dns_ipv4_1 | `1.0.0.1` | Cloudflare [DNS server](https://1.1.1.1/)
| dns_ipv4_1 | `2606:4700:4700::1111` | Cloudflare [DNS server](https://1.1.1.1/)
| dns_ipv4_1 | `2606:4700:4700::1001` | Cloudflare [DNS server](https://1.1.1.1/)
| wireguard_allowed_ipv4 | `0.0.0.0/0` | IPv4 addresses that are routed through the VPN. The default routes everything through the VPN.
| wireguard_allowed_ipv6 | `::/0` | IPv6 addresses that are routed through the VPN. The default routes everything through the VPN.

Additionally, if clients should be added with this role a dictionary like the following one is required:

```yaml
peers_list:
  - username: '<username>'
    device: '<device>'
    wireguard_client_key: '<generate with: "umask 077; wg genkey > wg-vpn.key && echo -n "Secret Wireguard Key: " | cat - wg-vpn.key">'
    wireguard_client_pub: '<optional - generate with: "wg pubkey < wg-vpn.key > wg-vpn.pub && echo -n "Public Wireguard Key: " | cat - wg-vpn.pub">'
    wireguard_client_id: <number between 1 and 253>
```

The `wireguard_client_id` must be unique and in the **range between 1 and 253**. 
This ID will be used to assign an IPv4 and IPv6 address to the peer. 
**The `wireguard_client_key` is optional**. A user can send you his public key and you create then the config file without the private key. 
Send this configuration file back to the user, so that he can add his private key to connect to your VPN server.

To create the keys you can use either the single commands above or this one-liner:

```sh
$ umask 077; wg genkey > wg-vpn.key && echo -n "Secret Wireguard Key: " | cat - wg-vpn.key && wg pubkey < wg-vpn.key > wg-vpn.pub && echo -n "Public Wireguard Key: " | cat - wg-vpn.pub
```

Unlike other roles this one does not use the `wg-quick` command to add peers. 
This one uses `syncconf`:

> Man page for [wg(8)](https://manpages.debian.org/unstable/wireguard-tools/wg.8.en.html)
>
>  [syncconf] reads back the existing configuration first and only makes changes that are explicitly different between the configuration file and the interface. This is much less efficient than setconf, but has the benefit of not disrupting current peer sessions.

Every time you run this role, a Wireguard configuration file with all peers will be generated when peers are added, removed or changed. 
This will trigger `syncconf` to execute the changes without disrupting connected peers.

Without the dictionary `peers_list` the Wireguard server itself will be installed and configured. 

## Dependencies

This role does not have any dependencies.

# Setup and Examples

## Installation

Clone or download this role into your `roles` folder.  

## Inventory
For this examples to work you need an inventory with a group called `wireguard`.

```yml
---
# hosts.yml
wireguard:
  hosts:
    wireguard_server:
      ansible_ssh_host: wireguard.example.com # Or use the IP address here
      ansible_ssh_port: 22
      ansible_ssh_user: root
```

## Example playbook without adding peers

As already mentioned, as long as no peers are added no additional parameters are required. 
Playbook without adding peers:

```yml
---
# wireguard-playbook.yml
- name: Setup and config Wireguard server
    hosts: wireguard
    become: yes
    roles:
        - ansible-wireguard
```

## Example playbook without adding peers but adding parameters

Let's change the port and the IPv4 address range:

```yml
---
# wireguard-playbook.yml
- name: Setup and config Wireguard server
    hosts: wireguard
    become: yes
    roles:
        - ansible-wireguard
  vars:
    - wireguard_network_ipv4: '10.42.42'
    - wireguard_port: '4242'
```

## Example playbook with peers

If we want to add some peers, we can use the following play:

```yml
---
# wireguard-playbook.yml
- name: Setup and config Wireguard server
    hosts: wireguard
    become: yes
    roles:
        - wireguard
    vars:
      peers_list:
        - username: 'johndoe'
          device: 'mbp15'
          wireguard_client_key: 'q3498rhfiuber98fn43qc98qe4'
          wireguard_client_pub: 'nu43p98fnf4nq3n3q84nf83n43'
          wireguard_client_id: 1
        - username: 'janedoe'
          device: 'ipad'
          wireguard_client_pub: '09i43fn98noinrew98wifoijij'
          wireguard_client_id: 2
```

This play will configure the server and add two peers for John and Jane Doe. 
The config files will be stored locally  if `wireguard_client_files_remote` is set to `false` and should have the following path and names:

- `./files-wireguard/wireguard.example.com/wg0_clients/johndoe/mbp15-US.conf`
- `./files-wireguard/wireguard.example.com/wg0_clients/janedoe/ipad-US.conf`

If the default setting for `wireguard_client_files_remote` remains unchanged the paths to the files are 

- `/etc/wireguard/wg0_clients/johndoe/` and 
- `/etc/wireguard/wg0_clients/janedoe/`.

## Example playbook with peers and parameters

Now we add the parameters for the network and port:

```yml
---
# wireguard-playbook.yml
- name: Setup and config Wireguard server
    hosts: wireguard
    become: yes
    roles:
        - ansible-wireguard
    vars:
      peers_list:
        - username: 'johndoe'
          device: 'mbp15'
          wireguard_client_key: 'q3498rhfiuberjustfake98fn43qc98qe4'
          wireguard_client_pub: 'nu43p98fnf4nq3njustfake3q84nf83n43'
          wireguard_client_id: 1
        - username: 'janedoe'
          device: 'ipad'
          wireguard_client_pub: '09ijustfakeeeal98noinrew98wifoijij'
          wireguard_client_id: 2
      wireguard_network_ipv4: '10.42.42'
      wireguard_port: '4242'
```

## Example playbook with separate files

For this example we need the dictionary for `peers_list` in a separate file. 
For example in a file called `wireguard.yml` and located in `host_vars`:

```yml
---
# wireguard.yml
peers_list:
  - username: 'johndoe'
    device: 'mbp15'
    wireguard_client_key: 'q3498rhfiuber98fn43qc98qe4'
    wireguard_client_pub: 'nu43p98fnf4nq3n3q84nf83n43'
    wireguard_client_id: 1
  - username: 'janedoe'
    device: 'ipad'
    wireguard_client_pub: '09i43fn98noinrew98wifoijij'
    wireguard_client_id: 2
wireguard_network_ipv4: '10.42.42'
wireguard_port: '4242'
```

And then we just run a playbook like in the example without adding peers:

```yml
# wireguard-playbook.yml
- name: Setup and config Wireguard server
    hosts: wireguard
    become: yes
    roles:
        - ansible-wireguard
```

## Connect and Verify

To connect with your Wireguard server use:

```sh
sudo wg-quick up <abs-or-rel-path-to-config-file>
```

And to disconnect just replace `up` with `down`:

```sh
sudo wg-quick down <abs-or-rel-path-to-config-file>
```

To verify your installation you can use [Browserleaks](https://browserleaks.com/ip) after a successful connection to your new VPN server.

# License

GPLv3, see [license](./LICENSE).

# Contributing

Feel free to open issues or merge requests if you find problems or have ideas for improvements. Thank you.