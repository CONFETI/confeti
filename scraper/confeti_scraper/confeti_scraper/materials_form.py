def materials_form(material_link: list) -> dict:
    res = {}
    if material_link is None:
        return
    for link in material_link:
        if 'youtu' in link:
            res['video'] = link
        elif 'github' in link:
            res['repo'] = link
        elif ('ctfas' or 'google') in link:
            res['presentation'] = ''.join(('https:',link))
        else:
            res['article'] = link
    return res
