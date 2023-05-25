import argparse
import json
from typing import List, Any, Dict, TextIO


def read_json(filename: str) -> Dict[str, Any]:
    with open(filename) as file:
        return json.load(file)


def satiate_aliases(aliases: Dict[str, Any], licenses: List[str]) -> List[str]:
    allowed_aliases = [aliases[x] for x in aliases if x in aliases and x in licenses]
    allowed_aliases_flatten = [item for sublist in allowed_aliases for item in sublist]
    return sorted(licenses + allowed_aliases_flatten)


def read_licenses():
    licenses = read_json('compliance/licenses-config.json')
    aliases = read_json('tools/aliases.json')['aliases']
    allowed_licenses = satiate_aliases(aliases, licenses['allowedLicenses'])
    forbidden_licenses = satiate_aliases(aliases, licenses['forbiddenLicenses'])
    assert len(set(allowed_licenses) & set(forbidden_licenses)) == 0
    return allowed_licenses, forbidden_licenses


def read_libs(platform: str) -> List[str]:
    libs = read_json('tools/allowed-libs.json')
    return [lib['name'] for lib in libs['libs'][platform]]


def write_statement(file: TextIO, statement: str, param: str):
    file.write(f'- - :{statement}\n')
    file.write('  - ' + param + '\n')


def write_allowed_libs(decisions: TextIO, allowed_libs: List[str]):
    for lib in allowed_libs:
        write_statement(decisions, statement="approve", param=lib)


def write_allowed_licenses(decisions: TextIO, allowed_licenses: List[str]):
    for license in allowed_licenses:
        write_statement(decisions, statement="permit", param=license)


def write_forbidden_licenses(decisions: TextIO, forbidden_licenses: List[str]):
    for license in forbidden_licenses:
        write_statement(decisions, statement="restrict", param=license)


def write_decisions(platform: str):
    allowed_licenses, forbidden_licenses = read_licenses()
    allowed_libs = read_libs(platform)

    with open("decisions.yml", "a") as decisions:
        decisions.write('---\n')

        write_allowed_licenses(decisions, allowed_licenses)
        write_forbidden_licenses(decisions, forbidden_licenses)
        write_allowed_libs(decisions, allowed_libs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='license validation generator')
    parser.add_argument('-p', '--platform', help='ios, android, golang', type=str, required=True)
    write_decisions(parser.parse_args().platform)
