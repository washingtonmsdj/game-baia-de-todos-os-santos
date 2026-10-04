"""Referências técnicas Toyota: dados nominais, mídia interna, sem arte de jogo."""
import urllib.request,json,hashlib
from pathlib import Path
repo=Path(__file__).resolve().parents[2]
root=repo/'world-reference/vehicles/hilux';root.mkdir(parents=True,exist_ok=True)
sources=[
('toyota-hilux-gx-side.jpg','https://images.toyota-europe.com/es/configurationtype/visual-for-grade-selector/product-token/6fa1b3ca-c11e-45bd-a72c-40098d0f2d1d/grade/d77d74f2-c4c0-4a88-b284-9105a8fe659c/body/f880e881-f794-4aef-9e12-db540db6d76d/fallback/true/width/928/height/556/scale-mode/0/padding/0/background-colour/FFFFFF/image-quality/75/exterior-9.jpg'),
('hilux-2024-ficha-tecnica.pdf','https://media.toyota.com.br/ac8fa1b8-e792-4e4a-81cf-3206c2cee7f4.pdf'),
('hilux-2024-std-lateral.jpg','https://files.agenciaarara.com.br/files/company/vehicle/cm0dvki52007hspaf2480nfgf/STD%20POWER%20PACK/03.Jpg.ixv7pq86c2sihumjomyjk833.jpg')
]
result=[]
for filename,url in sources:
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=15) as r:
            data=r.read()
        dest=root/filename;dest.write_bytes(data)
        result.append({'file':dest.relative_to(repo/'world-reference').as_posix(),'url':url,'sha256':hashlib.sha256(data).hexdigest(),'usage_class':'REFERENCIA_INTERNA','license_status':'pending'})
    except Exception as e:result.append({'url':url,'error':type(e).__name__+': '+str(e)})
path=repo/'world/vehicles/hilux-dimensions.json'
path.write_text(json.dumps({'asset_id':'vehicle-rondesp-pickup','source_url':sources[1][1],'source_name':'Toyota do Brasil, ficha técnica Hilux 2024 STD Power Pack','dimensions_m':{'length':5.325,'body_width_without_mirrors':1.855,'stock_vehicle_height':1.815,'wheelbase':3.085,'cargo_internal_length':1.569,'cargo_internal_width':1.645,'cargo_internal_height':.481},'tires':{'designation':'265/65 R17','width_m':.265,'rim_diameter_m':.4318,'nominal_unloaded_radius_m':.38815},'application_notes':'Medidas nominais do veículo base. Capota, antena, estribos e quebra-mato policiais não medidos; altura/contorno desses acessórios continuam candidatos. Modelo fotografado 2024/2025 conforme legenda do usuário; não confirmação da versão via VIN.','media_acquisition':result},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
