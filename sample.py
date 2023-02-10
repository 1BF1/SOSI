from flask import Flask, request, render_template, redirect
import pandas as pd

def test(dict1, dict2):
    x = len(dict1) - len(dict2)
    for i in range(x):
        dict2.append('None')
    return dict2

def check_sosi(file_content, filename):

    dict_test = {}

    
    for line in file_content:
        if not ".." in line:
            if "." in line:
                dict_name = line.strip().replace(".", "").replace(":", "")
                dict_test[dict_name] = []
        line = line.strip().replace(".", "")
        if not line.replace(":", "") == dict_name:
            dict_test[dict_name].append(line)

    dict_kontroll = {'Navn': [], 'PTEMA/LTEMA': [], 'OBJTYPE': [], 'KATEGORI/BESKRIVELSE': [], 'INFO': []}
    for key in dict_test:
        tema = ""
        obj = ""
        kat = ""
        fid = ""
        if not key == 'HODE':
            if not key == 'SLUTT':
                dict_kontroll['Navn'].append(key)
                for value in dict_test[key]:
                    if 'PTEMA' in value or 'LTEMA' in value:
                        ptma = value.split(" ")
                        if len(ptma) > 0:
                            tema = tema + ptma[1] + " "
                        else:
                            tema = tema + 'None '
                    if 'OBJTYPE' in value:
                        pobj = value.split(" ")
                        if len(pobj) > 0:
                            obj = obj + pobj[1] + " "
                        else:
                            obj = obj + 'None '
                    if 'KATEGORI' in value or 'BESKRIVELSE' in value:
                        pkat = value.split(" ")
                        if len(pkat) > 0:
                            kat = kat + str(pkat[1:]).strip().replace(",", "").replace("[", "").replace("]", "").replace("'", "").replace('"', "") + " "
                        else:
                            kat = kat + 'None '
                    if 'INFO' in value:
                        pfid = value.split(" ")
                        if len(pfid) > 0:
                            fid = fid + str(pfid[1:]).strip().replace(",", "").replace("[", "").replace("]", "").replace("'", "").replace('"', "") + " "
                        else:
                            fid = fid + 'None '
                if not tema == "":
                    dict_kontroll['PTEMA/LTEMA'].append(tema)
                if not obj == "":
                    dict_kontroll['OBJTYPE'].append(obj)
                if not kat == "":
                    dict_kontroll['KATEGORI/BESKRIVELSE'].append(kat)
                if not fid == "":
                    dict_kontroll['INFO'].append(fid)
    if not len(dict_kontroll['Navn']) == len(dict_kontroll['PTEMA/LTEMA']):
        dict_kontroll['PTEMA/LTEMA'] = test(dict_kontroll['Navn'], dict_kontroll['PTEMA/LTEMA'])
    if not len(dict_kontroll['Navn']) == len(dict_kontroll['OBJTYPE']):
        dict_kontroll['OBJTYPE'] = test(dict_kontroll['Navn'], dict_kontroll['OBJTYPE'])
    if not len(dict_kontroll['Navn']) == len(dict_kontroll['KATEGORI/BESKRIVELSE']):
        dict_kontroll['KATEGORI/BESKRIVELSE'] = test(dict_kontroll['Navn'], dict_kontroll['KATEGORI/BESKRIVELSE'])
    if not len(dict_kontroll['Navn']) == len(dict_kontroll['INFO']):
        dict_kontroll['INFO'] = test(dict_kontroll['Navn'], dict_kontroll['INFO'])
    df = pd.DataFrame.from_dict(dict_kontroll)

    koord = ""
    for value in dict_test['HODE']:
        if 'KOORDSYS' in value:
            koord = value

    html = df.to_html(index=False)
    alfa1 = True
    test_bool = True
    erro_kode = ""
    for value in dict_kontroll['PTEMA/LTEMA']:
        if not value.strip().isnumeric():
            erro_kode = erro_kode + "(Feil PTEMA/LTEMA) "
            test_bool = False
            alfa1 = False
            break
    for value in dict_kontroll['OBJTYPE']:
        if not "Trase" in str(value):
            erro_kode = erro_kode + "(Feil OBJTYPE) "
            test_bool = False
            break
    for value in dict_kontroll['KATEGORI/BESKRIVELSE']:
        if 'Udefinert' in str(value) or 'None' in str(value):
            erro_kode = erro_kode + "(Mangler BESKRIVELSE) "
            test_bool = False
            break
    if len(koord.split(" ")) == 1:
        erro_kode = erro_kode + "(Mangler KOORDSYS) "
        test_bool = False
    dict_feil_tema = {'Linje': [], 'Feil beskrivelse': [],'Korrekt beskrivelse': []}
    if alfa1:
        dict_feil_tema = {'Linje': [], 'Feil beskrivelse': [],'Korrekt beskrivelse': []}
        input_beskrivelse = dict_kontroll['KATEGORI/BESKRIVELSE']
        input_tema = dict_kontroll['PTEMA/LTEMA']
        dict_ptma_master = {'PTEMA/LTEMA': ['801','802','803','807','808','810','814','820','859','860','804','812','850','851','852','874','877','878'],'KATEGORI/BESKRIVELSE': ['Fiber rør i rør','Fiber rør i gassrør','Fiber i rør','Fiber reserverør','Fiber lokalnett','Fiber stikkledning i rør','Fiber uten rør','Fiber microtrench','Fiber omriss nodehytte','Fiber omriss kum','Fiber skjøt','Fiber ende rør','Fiber kum','Fiber stolpe','Fiber stolpe med kveileramme','Fiber kundepunkt','Fiber skap','Fiber kveil rør']}
        for i in range(len(input_tema)):
            if input_tema[i].strip() in dict_ptma_master['PTEMA/LTEMA']:
                index_master = dict_ptma_master['PTEMA/LTEMA'].index(input_tema[i].strip())
                if not input_beskrivelse[i].strip() == dict_ptma_master['KATEGORI/BESKRIVELSE'][index_master]:
                    dict_feil_tema['Linje'].append(str(int(i) + 1))
                    dict_feil_tema['Feil beskrivelse'].append(input_beskrivelse[i])
                    dict_feil_tema['Korrekt beskrivelse'].append(dict_ptma_master['KATEGORI/BESKRIVELSE'][index_master])
            else:
                dict_feil_tema['Linje'].append(str(i))
                dict_feil_tema['Feil beskrivelse'].append(['PTEMA/LTEMA finnes ikke (SOSI Spesifikasjon)'])
                dict_feil_tema['Korrekt beskrivelse'].append(['PTEMA/LTEMA finnes ikke (SOSI Spesifikasjon)'])
                    

    if dict_feil_tema['Linje']:
        dict_html = pd.DataFrame.from_dict(dict_feil_tema).to_html(index=False)
        return dict_html + pd.DataFrame.from_dict({filename: [], koord: []}).to_html(index=False) + html + '<br><br>'
    else: 
        if test_bool == True:
            return pd.DataFrame.from_dict({filename: [], koord: []}).to_html(index=False) + html + '<br><br>'
        else:
            dict_erro = {}
            for i in erro_kode.split(")"):
                if len(i) > 4:
                    dict_erro[i.replace("(", "")] = []
            erro_html = pd.DataFrame.from_dict(dict_erro).to_html(index=False)
            return erro_html + pd.DataFrame.from_dict({filename: [], koord: []}).to_html(index=False) + html + '<br><br>'

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_sosi_test', methods=['POST'])
def run_sosi_test():
    files = request.files.getlist('file')
    file_contents = []
    html = ""
    for file in files:
        if file and file.filename.endswith('.sos'):
            html = html + check_sosi(file.read().decode('ISO-8859-1').split("\n"), file.filename)

    if file and file.filename.endswith('.sos'): 
        ex_dict = {'Navn': ['KURVE 1', 'KURVE 2','PUNKT 3', 'PUNKT 4'], 'PTEMA/LTEMA': ['810','803','877', '850'], 'OBJTYPE': ['Trase','Trase','Trasepunkt', 'Trasepunkt'], 'BESKRIVELSE': ['Fiber i luft','Fiber i rør','<skap nr> f.eks: H2234', '<kum nr> f.eks:K2342'], 'INFO': ['1x40mm 2x20mm','1x40mm 2x20mm','<Type skap>', 'KUM']}
        send_html = '<br><br><br><br>' + pd.DataFrame.from_dict({'Ønsket resultat:': [], 'KOORDSYS 22': []}).to_html(index=False) + pd.DataFrame.from_dict(ex_dict).to_html(index=False) + '<br><br>' + html 
        return render_template('result.html', file_contents=send_html)
    else: 
        return render_template('feil.html')
    

if __name__ == '__main__':
    app.run(debug=True)




