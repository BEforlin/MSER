import cv2
import numpy as np
import sys
from copy import copy, deepcopy
import time

def filter_seed(seed_list, seed_list_filtered, size_min, size_max):
    count = 0
    for key, value in seed_list.iteritems():
        if (((1-value) >= size_min) and ((1-value) < size_max)):
            seed_list_filtered[key] = value
    return seed_list_filtered

def get_coordinate(position, Width): #GRADE COMECA NA POSICAO X=0 Y=0
    "Returns x and y positions for a given position, returns a list"
    i = int(position%Width)
    j = int((position-i)/Width)
    x_and_y  = [i, j]
    return x_and_y

def growth_rate(Q_prev, Q_curr, Q_fut, acceptable_growth, size_min, size_max, f2):
    "Calculates maximun acceptable growth rate"
    for key, value in Q_curr.iteritems():
        try:
            a = Q_prev[key]
        except KeyError:
            return acceptable_growth
        try:
            b = Q_fut[key]
        except KeyError:
            return acceptable_growth
        if (((1-int(a)) >= size_min) and ((1-int(b)) < size_max)):
            if (float(((1-b)-(1-a))/Q_curr[key]) <= 0.5):
                #print >> f2, "variation: ", float(((1-b)-(1-a))/Q_curr[key])
                acceptable_growth[key] = Q_curr[key]
    return acceptable_growth

def paint_acceptable_growth(acceptable_growth,region_map, Width, paint_map, size_min, size_max):
    "paints max stable region"
    for key, value in acceptable_growth.iteritems():
        i = get_coordinate(key, Width)[0]
        j = get_coordinate(key, Width)[1]
        valor = region_map[3, j, i]
        if (((1-int(region_map[2, j, i])) >= size_min) and ((1-int(region_map[2, j, i])) < size_max)):
            for num_elem in xrange(1-int(region_map[2, j, i])):                                                       #loop que muda a seed de todos os px da regiao sendo eliminada
                i_it = get_coordinate(valor, Width)[0]
                j_it = get_coordinate(valor, Width)[1]
                valor = region_map[3, j_it, i_it]
                paint_map[j_it, i_it] = 130
    return paint_map

def preprocessing(Height, Width, im, region_map):

    histogram = np.zeros(256)
    culmulative = np.zeros(256)
    position_vector = np.zeros(Height*Width)
    keep_track = np.zeros(256)

    culm = 0
    index = 0

    for i in xrange(Height):                                                    #troca os valore RGB
        for j in xrange(Width):
            px = im[i,j]
            #im2[i,j] = im[i,j]
            px[0] = px[1] = px[2] = px[2]*0.2126 + px[1]*0.7152 + px[0]*0.0722  #opencv usa BGR
            histogram[px[0]] = histogram[px[0]] + 1
            im[i,j] = px

    for i in histogram:                                                         #histograma culmulativo
        culmulative[index] = culm
        culm = culm + i
        index = index + 1
    for i in xrange(Height):                                                    #organiza o vetor de posicoes
        for j in xrange(Width):
            px = im[i,j]
            position_vector[int(culmulative[px[0]]+keep_track[px[0]])] = i*Width+j
            keep_track[px[0]] = keep_track[px[0]] + 1

    for i in xrange(Width):
        for j in xrange(Height):
            region_map[0,j,i] = 255

    return position_vector, histogram, im, region_map

def union_find(i, j, Width, size_min, size_max, region_map, seed_list, x, y, f1, f2):
    "Runs the union_find algorithm (in progress)"
    try:
        region_map[0, j+y, i+x]
    except IndexError:
        return region_map, seed_list

    if (not(region_map[1, j, i])):  #cria link se nao foi visitado ainda
        region_map[3, j, i] = Width*j+i

    if (not(region_map[0, j+y, i+x]) or (region_map[0, j+y, i+x]==130)):   #se vizinho existe
        if (region_map[1, j+y, i+x]):    #se vizinho jah foi visitado
            if (region_map[1, j, i]):     #se pixel atual tem seed:
                if (region_map[2, j, i] <= 0):
                    i_seed = i
                    j_seed = j
                else:
                    i_seed = get_coordinate(region_map[2, j, i], Width)[0]
                    j_seed = get_coordinate(region_map[2, j, i], Width)[1]
                if (region_map[2, j+y, i+x] <= 0):
                    i_seed_viz = i + x
                    j_seed_viz = j + y
                else:
                    i_seed_viz = get_coordinate(region_map[2, j+y, i+x], Width)[0]
                    j_seed_viz = get_coordinate(region_map[2, j+y, i+x], Width)[1]
                if ((i_seed == i_seed_viz) and (j_seed == j_seed_viz)):         #checa se pixel jah nao pertence a essa regiao
                    region_map[1, j, i] = 1                                                                                                 #marca px atual como visitado
                    i_seed = get_coordinate(region_map[2, j, i], Width)[0]
                    j_seed = get_coordinate(region_map[2, j, i], Width)[1]
                    return region_map, seed_list
                if (region_map[2, j_seed, i_seed] >= region_map[2, j_seed_viz, i_seed_viz]):#se seed da regiao atual menor ou igual regiao vizinha:
                    region_map[2, j_seed_viz, i_seed_viz] = region_map[2, j_seed, i_seed] + region_map[2, j_seed_viz, i_seed_viz] -1        #tamanho regiao vizinha atualizado
                    valor = region_map[3, j_seed, i_seed]
                    seed_list[Width*j_seed_viz+i_seed_viz] = region_map[2, j_seed_viz, i_seed_viz] #update regiao mantida
                    try:
                        del seed_list[Width*j_seed+i_seed] #deleta entrada antiga
                    except KeyError:
                        pass
                    size = 1-int(region_map[2, j_seed, i_seed])
                    for num_elem in xrange(size):                                                           #loop que muda a seed de todos os px da regiao sendo eliminada
                        i_temp = get_coordinate(valor, Width)[0]
                        j_temp = get_coordinate(valor, Width)[1]
                        region_map[2, j_temp, i_temp] = Width*j_seed_viz+i_seed_viz
                        valor = region_map[3, j_temp, i_temp]
                else:   #se seed da regiao atual maior q regiao vizinha:
                    region_map[2, j_seed, i_seed] = region_map[2, j_seed, i_seed] + region_map[2, j_seed_viz, i_seed_viz] -1                #tamanho regiao atual atualizado
                    valor = region_map[3, j_seed_viz, i_seed_viz]
                    seed_list[Width*j_seed+i_seed] = region_map[2, j_seed, i_seed] #update regiao mantida
                    try:
                        del seed_list[Width*j_seed_viz+i_seed_viz] #deleta entrada antiga
                    except KeyError:
                        pass
                    size = 1-int(region_map[2, j_seed_viz, i_seed_viz])
                    for num_elem in xrange(size):                                                   #loop que muda a seed de todos os px da regiao sendo eliminada
                        i_temp = get_coordinate(valor, Width)[0]
                        j_temp = get_coordinate(valor, Width)[1]
                        region_map[2, j_temp, i_temp] = Width*j_seed+i_seed
                        valor = region_map[3, j_temp, i_temp]
                #faz um swap dos links dos seeds das regioes:
                temp = region_map[3, j_seed, i_seed]
                region_map[3, j_seed, i_seed] = region_map[3, j_seed_viz, i_seed_viz]
                region_map[3, j_seed_viz, i_seed_viz] = temp
            else:   #se px atual nao tem seed:
                if (region_map[2, j+y, i+x] <= 0): #testa se vizinho eh seed
                    i_seed_viz = i + x
                    j_seed_viz = j + y
                else:
                    i_seed_viz = get_coordinate(region_map[2, j+y, i+x], Width)[0]
                    j_seed_viz = get_coordinate(region_map[2, j+y, i+x], Width)[1]
                region_map[2, j, i] = int(Width*(j_seed_viz)+i_seed_viz)                                                                    #px atual se une a regiao vizinha
                region_map[2, j_seed_viz, i_seed_viz] = region_map[2, j_seed_viz, i_seed_viz] - 1                                           #atualiza U do seed de regiao vizinha
                seed_list[int(region_map[2, j, i])] = region_map[2, j_seed_viz, i_seed_viz]
                region_map[3, j, i] = region_map[3, j_seed_viz, i_seed_viz]                                                                 #px atual recebe link do seed de regiao vizinha
                region_map[3, j_seed_viz, i_seed_viz] = int(Width*(j)+i)                                                                    #seed de regiao vizinha recebe link de px atual
        else:   #se vizinho nao foi visitado:
            region_map[3, j+y, i+x] = Width*(j+y)+i+x#cria link do vizinho nao visitado
            if (region_map[2, j, i] == 0):  #se pixel atual nao tem seed:
                region_map[2, j+y, i+x] = int(Width*j+i)                                                                                    #cria regiao e adiciona vizinho(pixel atual vira Seed)
                #seed_list_filtered = seed_list_filtered +1
                seed_list[int(region_map[2, j+y, i+x])] = region_map[2, j, i] =  - 1                                                                      #cria U da Seed da regiao atual
                region_map[3, j+y, i+x] = int(Width*j+i)                                                                                    #vizinho recebe link para px atual
                region_map[3, j, i] = int(Width*(j+y)+i+x)                                                                                  #px atual recebe link para px vizinho
            else:   #se px atual tem seed:
                if (region_map[2, j, i] < 0):   #teste se atual eh seed
                    i_seed = i
                    j_seed = j
                else:
                    i_seed = get_coordinate(region_map[2, j, i], Width)[0]
                    j_seed = get_coordinate(region_map[2, j, i], Width)[1]
                region_map[2, j+y, i+x] = int(Width*(j_seed)+i_seed)                                                                        #add vizinho a regiao atual
                region_map[2, j_seed, i_seed] = region_map[2, j_seed, i_seed]- 1                                                            #atualiza regiao atual
                seed_list[int(region_map[2, j+y, i+x])] = region_map[2, j_seed, i_seed]   #update seed list
                region_map[3, j+y, i+x] = region_map[3, j_seed, i_seed]                                                                     #px vizinho recebe link do seed de regiao atual
                region_map[3, j_seed, i_seed] = int(Width*(j+y)+i+x)
            region_map[1, j+y, i+x] = 1                                                                                                     #marca vizinho como visitado
    #else:
        #print >> f2, "sem vizinho"
    region_map[1, j, i] = 1                                                                                                                 #marca px atual como visitado

    #aquisicao da lista de regiaos:
    # if (region_map[2, j, i]==0):
    #     i_teste = get_coordinate(region_map[3, j, i], Width)[0]
    #     j_teste = get_coordinate(region_map[3, j, i], Width)[1]
    # elif(region_map[2, j, i]>0):
    #     i_teste = get_coordinate(region_map[2, j, i], Width)[0]
    #     j_teste = get_coordinate(region_map[2, j, i], Width)[1]
    # else:
    #     i_teste = i
    #     j_teste = j
    # valor = region_map[3, j_teste, i_teste]
    # if ((1-int(region_map[2, j_teste, i_teste]) >= size_min) and ((1-int(region_map[2, j_teste, i_teste]) < size_max))):
    #     absorb = region_map[3, :, :]
        # for num_elem in xrange(1-int(region_map[2, j_teste, i_teste])):                                                       #loop que muda a seed de todos os px da regiao sendo eliminada
        #     i_temp = get_coordinate(valor, Width)[0]
        #     j_temp = get_coordinate(valor, Width)[1]
        #     valor = region_map[3, j_temp, i_temp]
        #     region_map[0, j_temp, i_temp] = 130
    return region_map, seed_list

def main(argv):

    image_name = "megateste"
    im = cv2.imread(str(image_name) + ".bmp")
    path = '/home/bforlin/MSER_total/out_images/'

    f1 = open('f1', 'w+')
    f2 = open('f2', 'w+')

    b = 0
    seed_list = {}
    seed_list_filtered = {}
    acceptable_growth = {}
    Q_curr = {}
    Q_fut = {}

    # Height = 240
    # Width = 320
    Height = 1080
    Width = 1920

    size_min = 121
    size_max = 8500

    region_map = np.zeros((4, Height, Width))
    #primeira camada (camada visivel), pixel pintado na RM (PX)
    #segunda camada pixel visitado pelo UF (UF_M)
    #terceira camada Seed do pixel (U)region_map[0, j, i] = 0
    #|PX         POS|
    #|      U       |
    #|LINK        UF|
    #|--------------|

    position_vector, histogram, im, region_map = preprocessing(Height, Width, im, region_map)
    cv2.imwrite(str(path) + str(image_name) + "_bw.bmp", im)                                         #cria o bmp em grayscale

    for num_pix in histogram:                                                   #itera pelas intensidades
        for a in xrange(int(num_pix)):                                          #marca pixeis dessa intensidade na camada visivel (PX)
            i = int(position_vector[int(a+b)]%Width)
            j = int((position_vector[int(a+b)]-i)/Width)
            region_map[0, j, i] = 0
        #checa se encontra regioes ja criadas
        for a in xrange(int(num_pix)):                                          #itera pelos pixeis adicionados nessa intensidade
            i = int(position_vector[int(a+b)]%Width)
            j = int((position_vector[int(a+b)]-i)/Width)
            region_map, seed_list = union_find(i, j, Width, size_min, size_max, region_map, seed_list, 0, 1, f1, f2)              #vizinho norte
            region_map, seed_list = union_find(i, j, Width, size_min, size_max, region_map, seed_list,0, -1, f1, f2)             #vizinho sul
            region_map, seed_list = union_find(i, j, Width, size_min, size_max, region_map, seed_list,1, 0, f1, f2)              #vizinho leste
            region_map, seed_list = union_find(i, j, Width, size_min, size_max, region_map, seed_list,-1, 0, f1, f2)             #vizinho oeste

        Q_prev  = Q_curr.copy()
        Q_curr = Q_fut.copy()
        seed_list_filtered = filter_seed(seed_list, seed_list_filtered, size_min, size_max)
        Q_fut = seed_list_filtered.copy()
        acceptable_growth = growth_rate(Q_prev, Q_curr, Q_fut, acceptable_growth, size_min, size_max, f2)

        print (int(b/(Height*Width)*100)), "%"
        b = b + num_pix                                                         #incrementa valor b
        paint_map = deepcopy(region_map[0, :, :])
        paint_map = paint_acceptable_growth(acceptable_growth, region_map, Width, paint_map, size_min, size_max)
        im3 = paint_map[:,:]#visual
        cv2.imwrite(str(path) + "im_" + str(b) + ".bmp", im3)#visual

    im3 = region_map[0,:,:]
    cv2.imwrite(str(path) + "im_" + str(image_name) + ".bmp", im3)
    f1.close()
    f2.close()
    pass

if __name__ == "__main__":
    start_time = time.time()
    main(sys.argv)
    print("--- %s seconds ---" % (time.time() - start_time))
