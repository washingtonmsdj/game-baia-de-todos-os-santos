"""DEM nas sondagens B93, usando somente o SSOT; não corrige altitudes."""
import json,math,hashlib
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[2]
ssot=json.loads((root/'world/geographic-reference.json').read_text());fit=ssot['horizontal']['transform'];vertical=ssot['vertical']['candidate_dem_to_scene']
controls=json.loads((root/'docs/reports/blender/lacerda-placement-b93/surfaces.json').read_text())
M=json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']
theta=math.radians(fit['rotation_epsg3857_to_blender_deg']);cos,sin=math.cos(theta),math.sin(theta);scale=fit['scale_blender_units_per_meter'];trans=fit['translation_blender']
paths=[root/'world-reference/centro-lapa-tororo-fontenova/source'/p/'terrain.tif' for p in ('osm-mapzen-20261005T045222Z','aleph-geotiff-20261005T150330Z')]
datasets=[]
for path in paths:
    im=Image.open(path);ps=im.tag_v2[33550];tie=im.tag_v2[33922];keys=im.tag_v2[34735];entries={keys[4+i*4]:list(keys[5+i*4:8+i*4]) for i in range(keys[3])}
    assert entries.get(3072)==[0,1,3857] and im.mode=='F'
    kind=entries.get(1025);assert kind in ([0,1,1],[0,1,2]);shift=.5 if kind==[0,1,2] else 0
    pix=im.load();nodata=float(im.tag_v2[42113]) if 42113 in im.tag_v2 else None
    rows=[]
    for row in controls['samples']:
        x,y=row['xy'];wx=M[0][0]*x+M[0][1]*y+M[0][3];wy=M[1][0]*x+M[1][1]*y+M[1][3];dx=(wx-trans[0])/scale;dy=(wy-trans[1])/scale
        ex=cos*dx+sin*dy;ey=-sin*dx+cos*dy
        col=(ex-tie[3])/ps[0]+tie[0]+shift;rr=(tie[4]-ey)/ps[1]+tie[1]+shift;c0=math.floor(col);r0=math.floor(rr);tx=col-c0;ty=rr-r0;z=None
        if 0<=c0<im.width-1 and 0<=r0<im.height-1:
            values=[float(pix[c,r]) for r in (r0,r0+1) for c in (c0,c0+1)]
            if all(math.isfinite(v) and v!=nodata for v in values):z=(values[0]*(1-tx)+values[1]*tx)*(1-ty)+(values[2]*(1-tx)+values[3]*tx)*ty
        rows.append({'control_id':row['id'],'world_xy':[wx,wy],'epsg3857':[ex,ey],'dem_m':z,'candidate_scene_z_NOT_APPLIED':z*vertical['scale_z_blender_units_per_dem_meter']+vertical['z_offset_blender_units'] if z is not None else None})
    with path.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
    datasets.append({'file':path.relative_to(root).as_posix(),'sha256':digest,'pixel_size_projected_m':list(ps[:2]),'samples':rows,'absolute_altitude_verified':False})
data={'ssot_sha256':controls['ssot_sha256'],'scene_file':controls['file'],'datasets':datasets,'scene_changed':False,'conclusion':'DEM candidato e patamares autorais não equivalem a cotas de piso/as-built; usar como evidência, sem aplicar fit global.'}
out=root/'docs/reports/blender/lacerda-placement-b93/dem-controls.json';out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps([{'file':d['file'],'samples':[v for v in d['samples'] if v['control_id'] in ('existing_upper_entry_1','lower_floor_vertex_0','lower_floor_vertex_18')]} for d in datasets],ensure_ascii=False))
