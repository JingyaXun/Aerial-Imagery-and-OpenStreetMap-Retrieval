
import sys
import os

import requests
import cv2
import overpy
import matplotlib.pyplot as plt
import numpy

def aerialdata(save_path,map_size,map_area):

    url = 'http://dev.virtualearth.net/REST/v1/Imagery/Map/Aerial?'

    params = {
        'mapArea': f'{map_area[0]},{map_area[1]},{map_area[2]},{map_area[3]}',
        'mapSize': f'{map_size[0]},{map_size[1]}',
        'key': 'AmYCN1Z-zDj5P0Y-9Le_2qLWUXwHqBlJXqvo-ScJOlbV4dpMVefLxYI4UTfC7c6D',
    }

    response = requests.get(url, params=params)
    if("400" in response ):
        sys.stderr("unable to get image, please check map parameter")
        exit(-1)
    if("Bad Request".encode('gbk') in response.content):
        sys.stderr("unable to get image, please check map parameter")
        exit(-1)

    image_path = save_path+ "/step1img.jpg"

    with open(image_path, 'wb') as f:
        f.write(response.content)

    url = 'http://dev.virtualearth.net/REST/v1/Imagery/Map/Aerial?'

    params = {
        'mapArea': f'{map_area[0]},{map_area[1]},{map_area[2]},{map_area[3]}',
        'mapSize': f'{map_size[0]},{map_size[1]}',
        'mmd' : 1,
        'key': 'AmYCN1Z-zDj5P0Y-9Le_2qLWUXwHqBlJXqvo-ScJOlbV4dpMVefLxYI4UTfC7c6D',
    }

    response = requests.get(url, params=params)
    if("400" in response ):
        sys.stderr("unable to get image, please check map parameter")
        exit(-1)
    if("Bad Request".encode('gbk') in response.content):
        sys.stderr("unable to get image, please check map parameter")
        exit(-1)

    bbox = response.json()['resourceSets'][0]['resources'][0]['bbox']
    mapCenter = response.json()['resourceSets'][0]['resources'][0]['mapCenter']['coordinates']
    print(bbox)
    print(mapCenter)
    return bbox



def mapcut(savepath, bbox, map_area,map_size):
    image_path = savepath+"/step1img.jpg"
    img = cv2.imread(image_path)

    if img is None:
        sys.stderr('Map file doesnot exist')
        sys.exit(-1)

    height = img.shape[0]
    width =  img.shape[1]
    # print(bounding_box)
    # print(map_area)
    if(map_area[0]>height or map_area[1]>width):
        sys.stderr('invalid map size')
        sys.exit(-1)
    lat = (bbox[2] - bbox[0]) / height
    long = (bbox[3] - bbox[1]) / width
    top, left, bottom, right = 0, 0, 0, 0

    # print(lat)
    # print(long)

    for i in range(height):
        temp = bbox[0] + i*lat
        if temp > map_area[2]:
            bottom = i
            break

    for i in range(height):
        temp = bbox[0] + i*lat
        if temp > map_area[0]:
            top = i
            break

    for i in range(width):
        temp = bbox[1] + i*long
        if temp > map_area[3]:
            right = i
            break

    for i in range(width):
        temp = bbox[1] + i*long
        if temp > map_area[1]:
            left = i
            break

    # print(top)
    # print(bottom)
    # print(left)
    # print(right)
    map = img[top:bottom, left:right]
    imgpath = savepath + "/map.jpg"
    cv2.imwrite(imgpath, map)




def get_OSM(savepath,map_area):

    api = overpy.Overpass()
    area = f'{map_area[0]},{map_area[1]},{map_area[2]},{map_area[3]}'
    # print(area)
    response = api.query("""
        way(%s) ["highway"~"primary|secondary|tertiary|residential|cycleway|path"] ;
        (._;>;);
        out body;
        """%area)

    imgpath = savepath + "/map.jpg"
    img = cv2.imread(imgpath)
    if img is None:
        sys.stderr('Map file doesnot exist')
        sys.exit(-1)

    # print(img)
    background = numpy.zeros((img.shape[0],img.shape[1],img.shape[2]))
    height = img.shape[0]
    width =  img.shape[1]
    h1 = (map_area[2] - map_area[0]) / height
    w1 = (map_area[3] - map_area[1]) / width

    fig1 = plt.figure(1)
    plt.imshow(background)

    for way in response.ways:
        lats = []
        lons = []
        for node in way.nodes:
            lat = (map_area[2] - float(node.lat))/h1
            lon = (float(node.lon) - map_area[1])/w1
            if lat < 0 or lon < 0 or lat > height or lon > width:
                continue
            lats.append(lat)
            lons.append(lon)

        plt.plot(lons, lats)

    plt.axis('off')
    osmpath = savepath+"/OSM.jpg"
    plt.savefig(osmpath,bbox_inches='tight')

    plt.figure(2)
    b,g,r = cv2.split(img)

    img2 = cv2.merge([r,g,b])

    plt.imshow(img2)
    for way in response.ways:
        lats = []
        lons = []
        for node in way.nodes:
            lat = (map_area[2] - float(node.lat))/h1
            lon = (float(node.lon) - map_area[1])/w1
            if lat < 0 or lon < 0 or lat > height or lon > width:
                continue
            lats.append(lat)
            lons.append(lon)

        plt.plot(lons, lats) # , s=2, c='red', marker='o'

    plt.axis('off')
    imgpath = savepath + "/result.jpg"
    plt.savefig(imgpath,bbox_inches='tight',dpi=300)

    plt.show()
def main():
    if len(sys.argv) !=2 :
        sys.stderr.write("invalid parameters")
        sys.exit(-1)

    if len(sys.argv) == 2:
        if os.path.exists(sys.argv[1]) :
            savepath=sys.argv[1]
            map_size = [2000, 1400]
            map_area = [42.048733, -87.681739, 42.062893, -87.665217]
            #(55.947527, -3.205594), (55.952171, -3.195923)
            #（42.061741, -87.669484）（42.051090, -87.677284）
            #(38.892187, -77.053888), (38.886734, -77.038396)



            bbox = aerialdata(savepath,map_size,map_area)
            mapcut(savepath,bbox, map_area,map_size)
            get_OSM(savepath,map_area)
        else:
            sys.stderr.write("invalid path")
            sys.exit(-1)



if __name__ == '__main__':
    main()
