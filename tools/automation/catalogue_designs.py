"""Select catalogue cities without parsing every engineering register."""
import tomllib


def city_slug(path):
    in_city=False
    with path.open(encoding='utf-8') as stream:
        for line in stream:
            stripped=line.strip()
            if stripped.startswith('['):
                in_city=stripped.split('#',1)[0].strip()=='[city]'
            if in_city and stripped.startswith('slug') and '=' in stripped:
                value=tomllib.loads(line).get('slug')
                if isinstance(value,str) and value.strip():return value.strip()
    raise ValueError(f'{path}: missing city.slug')
