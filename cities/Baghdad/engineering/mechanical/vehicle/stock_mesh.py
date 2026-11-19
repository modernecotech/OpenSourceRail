"""Grouped cut-stock mesh in vehicle coordinates. Length unit is the metre."""
import math

import numpy as np


def assembly(stock, rig, geom, jambs, ends, braces):
    parts = []

    def extrude(name, loops, end, sides, position, basis):
        vertices = np.array([pt for x in (0,end) for loop in loops for y,z in loop for pt in [(x,y,z)]])
        vertices = vertices@np.array(basis)+position
        parts.append((name,vertices,sides))

    def member(name, key, start, end):
        start,end = np.array(start),np.array(end)
        delta = end-start
        length = np.linalg.norm(delta)
        ux = delta/length
        uy = np.array([0,1,0]) if abs(ux[1])<0.9 else np.array([-1,0,0])
        uz = np.cross(ux,uy)
        uy = np.cross(uz,ux)
        h,b,t = (v/1000 for v in stock["sections"][key])
        def ring(b,h):
            return [(-b/2,-h/2),(b/2,-h/2),(b/2,h/2),(-b/2,h/2)]
        faces = []
        for i in range(4):
            j=(i+1)%4
            faces += [(i,j,8+j,8+i), (4+j,4+i,12+i,12+j),
                      (i,i+4,j+4,j), (8+i,8+j,12+j,12+i)]
        extrude(name,[ring(b,h),ring(b-2*t,h-2*t)],length,faces,start,[ux,uy,uz])

    def plate(name, corners, vector):
        vertices = np.array(corners)
        vector = np.array(vector)
        # Winding consistent with the extrusion vector.
        if np.dot(np.cross(vertices[1]-vertices[0],vertices[2]-vertices[0]), vector)<0:
            vertices=vertices[::-1]
        n=len(vertices)
        faces=[tuple(reversed(range(n))), tuple(range(n,2*n))]
        for i in range(n):
            j=(i+1)%n
            faces.append((i,j,j+n,i+n))
        parts.append((name,np.concatenate([vertices,vertices+vector]),faces))

    def seat(name, key, x, y, bottom):
        l,b,t = (v/1000 for v in stock["seat_plates"][key])
        corners=[(x+dx*l/2,y+dy*b/2,bottom) for dx,dy in ((-1,-1),(1,-1),(1,1),(-1,1))]
        plate(name,corners,[0,0,t])

    body=stock["body"]
    side_y=body["side_axis_y_m"]
    sz=body["sill_axis_z_m"]
    cz=body["cantrail_axis_z_m"]
    bottom=sz+stock["sections"]["sill"][0]/2000
    top=cz-stock["sections"]["cantrail"][0]/2000
    for sy in (-side_y,side_y):
        for k in ("sill","cantrail"):
            height=body[k+"_axis_z_m"]
            splice=body[k+"_splice_x_m"]
            for a,b in ((-geom["car_body_length_m"]/2,splice),(splice,geom["car_body_length_m"]/2)):
                member(k,k,[a,sy,height],[b,sy,height])
        for x in jambs+ends:
            k="jamb" if x in jambs else "end_post"
            member(k,k,[x,sy,bottom],[x,sy,top])
        for a,b,cut in braces:
            length=math.hypot(b-a,cz-sz)
            c,s=abs(b-a)/length,(cz-sz)/length
            extra=stock["braced_revision"]["brace_end_clearance_m"]
            h=stock["sections"]["brace"][0]/2000
            start_trim=max((stock["sections"]["jamb"][0]/2000+h*s+extra)/c,
                           (stock["sections"]["sill"][0]/2000+h*c+extra)/s)
            direction=np.array([(b-a)/length,0,s])
            p=np.array([a,sy,sz])+direction*start_trim
            member("brace","brace",p,p+direction*cut)
            leg=stock["braced_revision"]["gusset_leg_m"]
            thick=stock["braced_revision"]["gusset_thickness_m"]
            for x,z,xsign,zsign in ((a,bottom,math.copysign(1,b-a),1),(b,top,math.copysign(1,a-b),-1)):
                for sign in (-1,1):
                    y=sy+sign*stock["sections"]["brace"][1]/2000
                    plate("gusset",[(x,y,z),(x+xsign*leg,y,z),(x,y,z+zsign*leg)],[0,sign*thick,0])
    for k,xs,chord,datum in (("floor_tie",jambs,"sill",bottom-stock["sections"]["floor_tie"][0]/2000),
                            ("end_tie",ends,"sill",sz),("bolster",geom["bogie_centres_m"],"sill",sz),
                            ("roof_tie",jambs+ends,"cantrail",cz)):
        width=side_y-stock["sections"][chord][1]/2000
        for x in xs:
            member(k,k,[x,-width,datum],[x,width,datum])
    bg=stock["bogie"]
    for pivot in geom["bogie_centres_m"]:
        for sign in (-1,1):
            pri=sign*rig["primary_seat_lateral_m"]
            sec=sign*rig["secondary_seat_lateral_m"]
            h=bg["side_axis_z_m"]
            member("bogie_side","bogie_side",[pivot-rig["frame_length_m"]/2,pri,h],
                   [pivot+rig["frame_length_m"]/2,pri,h])
            for dx in (-rig["wheelbase_m"]/2,rig["wheelbase_m"]/2):
                seat("primary_underside","primary_underside",pivot+dx,pri,h-stock["sections"]["bogie_side"][0]/2000
                     -stock["seat_plates"]["primary_underside"][2]/1000)
            dy=rig["primary_seat_lateral_m"]-stock["sections"]["bogie_side"][1]/2000
            tx=bg["transom_axis_x_m"]*sign+pivot
            member("transom","transom",[tx,-dy,bg["transom_axis_z_m"]],[tx,dy,bg["transom_axis_z_m"]])
            dx=bg["transom_axis_x_m"]-stock["sections"]["transom"][1]/2000
            z=bg["saddle_axis_z_m"]
            member("saddle","saddle",[pivot-dx,sec,z],[pivot+dx,sec,z])
            seat("secondary_top","secondary_top",pivot,sec,z+stock["sections"]["saddle"][0]/2000)
            seat("secondary_body","secondary_body",pivot,sec,sz-stock["sections"]["bolster"][0]/2000
                 -stock["seat_plates"]["secondary_body"][2]/1000)
    return parts


def serialize(parts):
    """Compute each piece's oriented mesh volume independently of stock section formulas."""
    lines=["# Baghdad quotation revision B. Metres. x forward, y left, z up, rail head z=0."]
    index=1
    volume=0
    for i,(name,vertices,faces) in enumerate(parts):
        lines.append(f"o {name}_{i:03d}")
        lines.extend("v {:.6f} {:.6f} {:.6f}".format(*v) for v in vertices)
        local=vertices-vertices[0]
        piece_volume=0
        for face in faces:
            lines.append("f "+" ".join(str(index+j) for j in face))
            f=local[list(face)]
            piece_volume += sum(np.dot(f[0],np.cross(f[k],f[k+1]))/6 for k in range(1,len(f)-1))
        if piece_volume <= 0:
            raise ValueError(f"Invalid mesh volume for {name}")
        volume += piece_volume
        index+=len(vertices)
    return "\n".join(lines)+"\n",float(volume)


def preview(parts):
    """Orthographic overview and bogie detail from the same assembled meshes."""
    from xml.etree.ElementTree import Element, SubElement, indent, tostring
    root = Element("svg", xmlns="http://www.w3.org/2000/svg", viewBox="0 0 1080 670",
                   role="img", attrib={"aria-labelledby":"caption"})
    SubElement(root,"title",id="caption").text="Baghdad braced body and powered bogie frame stock"
    SubElement(root,"rect",width="1080",height="670",fill="white")
    def label(x,y,msg,size=16,weight="normal"):
        el=SubElement(root,"text",{"x":str(x),"y":str(y),"font-size":str(size),
                      "font-family":"sans-serif","font-weight":weight,"fill":"#203547"})
        el.text=msg
    def panel(parts, origin, scale, group):
        tiles=[]
        for name, vv, faces in parts:
            v=vv-origin
            horizontal=v[:,0]+v[:,1]*0.42
            vertical=-v[:,2]-v[:,1]*0.43+v[:,0]*0.07
            depth=-v[:,0]*0.42+v[:,1]-v[:,2]*0.4594
            colours={"brace":"#3d8d84","gusset":"#70aca1","saddle":"#2b7775",
                     "secondary_top":"#d87528","primary_underside":"#f0a35b","secondary_body":"#d87528"}
            for f in faces:
                ids=list(f)
                pts=" ".join(f"{horizontal[j]*scale+group[0]:.2f},{vertical[j]*scale+group[1]:.2f}" for j in ids)
                tiles.append((float(np.mean(depth[ids])),pts,colours.get(name,"#8ba6b7")))
        for _,pts,col in sorted(tiles,key=lambda f:-f[0]):
            SubElement(root,"polygon",{"points":pts,"fill":col,"stroke":"#385466","stroke-width":"0.45"})
    bg={"bogie_side","transom","saddle","secondary_top","primary_underside"}
    label(44,40,"Baghdad steel frame quotation",27,"bold")
    label(44,70,"Revision B   /   Body and two bogie frames   /   Vehicle coordinates in metres")
    panel(parts,np.zeros(3),48,(535,303))
    label(44,348,"Four 1.30 m clear openings per side. Ten braces occupy the closed bays between and beyond the doors.")
    SubElement(root,"line",x1="44",y1="369",x2="1036",y2="369",stroke="#bacbd0")
    bogie=[p for p in parts if p[0] in bg and p[1][:,0].mean()>0]
    centre=np.mean([v[:,0].mean() for _,v,_ in bogie])
    panel(bogie,np.array([centre,0,0.5]),122,(290,506))
    label(566,435,"One bogie frame",22,"bold")
    label(566,477,"Two side rails, two transoms, two spring saddles.")
    label(566,511,"Orange pads locate four primary and two secondary seats.")
    label(566,546,"Wheelsets, drives, brakes and suspension await integration.")
    label(44,642,"Orthographic views of nominal steel pieces. Connections, fitted equipment and skin require separate geometry.",14)
    indent(root)
    return tostring(root,encoding="unicode")+"\n"
