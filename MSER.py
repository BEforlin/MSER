import cv2
import numpy as np
import sys

def get_coordinate(position, Width): #GRADE COMECA NA POSICAO X=1 Y=1
    "Returns x and y positions for a given position, returns a list"
    i = int(position%Width)
    j = int((position-i)/Width)
    x_and_y  = [i, j]
    return x_and_y

def union_find(i, j, Width, size_min, size_max, region_map, x, y, f1, f2_white):
    "Runs the union_find algorithm (in progress)"
    try:
        region_map[0, j+y, i+x]
    except IndexError:
        print >> f2_white, "vizinho nao existe"
        return region_map

    if (not(region_map[1, j, i])):  #cria link se nao foi visitado ainda
        region_map[3, j, i] = Width*j+i

    if (not(region_map[0, j+y, i+x]) or (region_map[0, j+y, i+x]==130)):   #se vizinho existe
    #if (region_map[0, j+y, i+x]):   #se vizinho existe
        print >> f2_white, "vizinho existe", ",vizinho = ", region_map[0, j+y, i+x]
        print >> f2_white, "atual:  i = ", i, "  j = ", j
        if (region_map[1, j+y, i+x]):    #se vizinho jah foi visitado
            #print >> f1, "vizinho foi visitado", ",visitado:",region_map[1, j+y, i+x] != 0
            if (region_map[1, j, i]):     #se pixel atual tem seed:
                #print >> f2_white, "vizinho foi visitado e px atual tem seed (REGION MERGE)", "seed atual:", region_map[2, j, i]
                if (region_map[2, j, i] <= 0):
                    #print >> f2_white, "Atual nao eh o seed, Seed = ", region_map[2, j, i]
                    i_seed = i
                    j_seed = j
                else:
                    #print >> f2_white, "Atual nao eh o seed, Seed = ", region_map[2, j, i]
                    i_seed = get_coordinate(region_map[2, j, i], Width)[0]
                    j_seed = get_coordinate(region_map[2, j, i], Width)[1]
                if (region_map[2, j+y, i+x] <= 0):
                    #print >> f2_white, "Vizinho eh o seed, Seed = ", region_map[2, j+y, i+x]
                    i_seed_viz = i + x
                    j_seed_viz = j + y
                else:
                    #print >> f2_white, "Vizinho nao eh o seed, Seed = ", region_map[2, j+y, i+x]
                    i_seed_viz = get_coordinate(region_map[2, j+y, i+x], Width)[0]
                    j_seed_viz = get_coordinate(region_map[2, j+y, i+x], Width)[1]
                if ((i_seed == i_seed_viz) and (j_seed == j_seed_viz)):         #checa se pixel jah nao pertence a essa regiao
                    #print >> f2_white, "jah pertence a regiao"
                    region_map[1, j, i] = 1                                                                                                 #marca px atual como visitado
                    i_seed = get_coordinate(region_map[2, j, i], Width)[0]
                    j_seed = get_coordinate(region_map[2, j, i], Width)[1]
                    return region_map
                if (region_map[2, j_seed, i_seed] >= region_map[2, j_seed_viz, i_seed_viz]):#se seed da regiao atual menor ou igual regiao vizinha:
                    #print >> f2_white, "regiao atual some", region_map[2, j_seed, i_seed], ">=", region_map[2, j_seed_viz, i_seed_viz]
                    region_map[2, j_seed_viz, i_seed_viz] = region_map[2, j_seed, i_seed] + region_map[2, j_seed_viz, i_seed_viz] -1        #tamanho regiao vizinha atualizado
                    valor = region_map[3, j_seed, i_seed]
                    for num_elem in xrange(1-int(region_map[2, j_seed, i_seed])):                                                           #loop que muda a seed de todos os px da regiao sendo eliminada
                        i_temp = get_coordinate(valor, Width)[0]
                        j_temp = get_coordinate(valor, Width)[1]
                        region_map[2, j_temp, i_temp] = Width*j_seed_viz+i_seed_viz
                        valor = region_map[3, j_temp, i_temp]
                else:   #se seed da regiao atual maior q regiao vizinha:
                    #print >> f2_white, "regiao vizinha some", region_map[2, j_seed, i_seed], "<", region_map[2, j_seed_viz, i_seed_viz]
                    region_map[2, j_seed, i_seed] = region_map[2, j_seed, i_seed] + region_map[2, j_seed_viz, i_seed_viz] -1                #tamanho regiao vizinha atualizado
                    valor = region_map[3, j_seed_viz, i_seed_viz]
                    for num_elem in xrange(1-int(region_map[2, j_seed_viz, i_seed_viz])):                                                   #loop que muda a seed de todos os px da regiao sendo eliminada
                        i_temp = get_coordinate(valor, Width)[0]
                        j_temp = get_coordinate(valor, Width)[1]
                        region_map[2, j_temp, i_temp] = Width*j_seed+i_seed
                        valor = region_map[3, j_temp, i_temp]
                #faz um swap dos links dos seeds das regioes:
                temp = region_map[3, j_seed, i_seed]
                region_map[3, j_seed, i_seed] = region_map[3, j_seed_viz, i_seed_viz]
                region_map[3, j_seed_viz, i_seed_viz] = temp
            else:   #se px atual nao tem seed:
                #print >> f2_white, "vizinho foi visitado e px atual sem seed"
                if (region_map[2, j+y, i+x] <= 0): #testa se vizinho eh seed
                    #print >> f2_white, "Vizinho eh o seed, Seed = ", region_map[2, j+y, i+x]
                    i_seed_viz = i + x
                    j_seed_viz = j + y
                else:
                    #print >> f2_white, "Vizinho nao eh o seed, Seed = ", region_map[2, j+y, i+x]
                    i_seed_viz = get_coordinate(region_map[2, j+y, i+x], Width)[0]
                    j_seed_viz = get_coordinate(region_map[2, j+y, i+x], Width)[1]
                region_map[2, j, i] = int(Width*(j_seed_viz)+i_seed_viz)                                                                    #px atual se une a regiao vizinha
                region_map[2, j_seed_viz, i_seed_viz] = region_map[2, j_seed_viz, i_seed_viz] - 1                                           #atualiza U do seed de regiao vizinha
                region_map[3, j, i] = region_map[3, j_seed_viz, i_seed_viz]                                                                 #px atual recebe link do seed de regiao vizinha
                region_map[3, j_seed_viz, i_seed_viz] = int(Width*(j)+i)                                                                    #seed de regiao vizinha recebe link de px atual
        else:   #se vizinho nao foi visitado:
            region_map[3, j+y, i+x] = Width*(j+y)+i+x#cria link do vizinho nao visitado
            #print >> f2_white, "vizinho nao foi visitado"
            if (region_map[2, j, i] == 0):  #se pixel atual nao tem seed:
                #print >> f2_white, "vizinho nao foi visitado e px atual sem seed", region_map[2, j, i]
                region_map[2, j+y, i+x] = int(Width*j+i)                                                                                    #cria regiao e adiciona vizinho(pixel atual vira Seed)
                region_map[2, j, i] =  - 1                                                                                                  #cria U da Seed da regiao atual
                region_map[3, j+y, i+x] = int(Width*j+i)                                                                                    #vizinho recebe link para px atual
                region_map[3, j, i] = int(Width*(j+y)+i+x)                                                                                  #px atual recebe link para px vizinho
            else:   #se px atual tem seed:
                #print >> f2_white, "vizinho nao foi visitado e px atual com seed", region_map[2, j, i]
                if (region_map[2, j, i] < 0):   #teste se atual eh seed
                    i_seed = i
                    j_seed = j
                else:
                    i_seed = get_coordinate(region_map[2, j, i], Width)[0]
                    j_seed = get_coordinate(region_map[2, j, i], Width)[1]
                region_map[2, j+y, i+x] = int(Width*(j_seed)+i_seed)                                                                        #add vizinho a regiao atual
                region_map[2, j_seed, i_seed] = region_map[2, j_seed, i_seed]- 1                                                            #atualiza regiao atual
                region_map[3, j+y, i+x] = region_map[3, j_seed, i_seed]                                                                     #px vizinho recebe link do seed de regiao atual
                region_map[3, j_seed, i_seed] = int(Width*(j+y)+i+x)
            region_map[1, j+y, i+x] = 1                                                                                                     #marca vizinho como visitado
    # else:
    #     print >> f2_white, "sem vizinho"
    region_map[1, j, i] = 1                                                                                                                 #marca px atual como visitado

    #aquisicao da lista de regiaos:
    if (region_map[2, j, i]==0):
        i_teste = get_coordinate(region_map[3, j, i], Width)[0]
        j_teste = get_coordinate(region_map[3, j, i], Width)[1]
    elif(region_map[2, j, i]>0):
        i_teste = get_coordinate(region_map[2, j, i], Width)[0]
        j_teste = get_coordinate(region_map[2, j, i], Width)[1]
    else:
        i_teste = i
        j_teste = j
    valor = region_map[3, j_teste, i_teste]
    # if (region_map[2, j_teste, i_teste]>0):
    #     print >> f2_white, "deu ruim"
    #     print >> f2_white, "U:",region_map[2, j_teste, i_teste], "     Link:", region_map[3, j_teste, i_teste]
    #     print >> f2_white, "i = ", i_teste, "  j = ", j_teste
    #teste_paulo = np.zeros((240, 320))
    #queijo = 0
    if ((1-int(region_map[2, j_teste, i_teste]) > size_min) and ((1-int(region_map[2, j_teste, i_teste]) < size_max))):
        for num_elem in xrange(1-int(region_map[2, j_teste, i_teste])):                                                       #loop que muda a seed de todos os px da regiao sendo eliminada
            i_temp = get_coordinate(valor, Width)[0]
            j_temp = get_coordinate(valor, Width)[1]
            valor = region_map[3, j_temp, i_temp]
            #print >> f2_white, "entrou no loop"
            #print >> f2_white, "U:",region_map[2, j_temp, i_temp], "     Link:", region_map[3, j_temp, i_temp]
            #print >> f2_white, "i = ", i_temp, "  j = ", j_temp
            region_map[0, j_temp, i_temp] = 130
            #teste_paulo[j_temp, i_temp] = 255
            #queijo = queijo + num_elem
        #im3 = teste_paulo[:,:]#vizual
        #cv2.imwrite("teste_paulo_" + str(queijo) + ".bmp", im3)#vizual
    return region_map


def main(argv):
    im = cv2.imread("tiger.bmp")

    f1 = open('f1', 'w+')
    f2_white = open('f2_white', 'w+')
    Height = 240
    Width = 320
    # Height = 2560
    # Width = 3840
    # Height = 736
    # Width = 736

    size_min = 121
    size_max = 8500

    histogram = np.zeros(256)
    culmulative = np.zeros(256)
    position_vector = np.zeros(Height*Width)
    keep_track = np.zeros(256)

    for i in xrange(Height):                                                    #troca os valore RGB
        for j in xrange(Width):
            px = im[i,j]
            #im2[i,j] = im[i,j]
            px[0] = px[1] = px[2] = px[2]*0.2126 + px[1]*0.7152 + px[0]*0.0722  #opencv usa BGR
            histogram[px[0]] = histogram[px[0]] + 1
            im[i,j] = px


    #cv2.imwrite("tiger_bw.bmp", im)                                         #cria o bmp em grayscale

    culm = 0
    index = 0
    for i in histogram:                                                         #histograma culmulativo
        culmulative[index] = culm
        culm = culm + i
        index = index + 1
    for i in xrange(Height):                                                    #organiza o vetor de posicoes
        for j in xrange(Width):
            px = im[i,j]
            position_vector[int(culmulative[px[0]]+keep_track[px[0]])] = i*Width+j
            keep_track[px[0]] = keep_track[px[0]] + 1

    #begin union find algorithm
    region_map = np.zeros((4, Height, Width))
    #primeira camada (camada visivel), pixel pintado na RM (PX)
    #segunda camada pixel visitado pelo UF (UF_M)
    #terceira camada Seed do pixel (U)region_map[0, j, i] = 0
    #|PX         POS|
    #|      U       |
    #|LINK        UF|
    #|--------------|

    b = 0
    Seeds = []
    treta = []
    for i in xrange(Width):
        for j in xrange(Height):
            region_map[0,j,i] = 255

    for num_pix in histogram:                                                   #itera pelas intensidades
        for a in xrange(int(num_pix)):                                          #marca pixeis dessa intensidade na camada visivel (PX)
            i = int(position_vector[int(a+b)]%Width)
            j = int((position_vector[int(a+b)]-i)/Width)
            region_map[0, j, i] = 0
            #region_map[0, j, i] = 255
        #checa se encontra regioes ja criadas
        for a in xrange(int(num_pix)):                                          #itera pelos pixeis adicionados nessa intensidade
            i = int(position_vector[int(a+b)]%Width)
            j = int((position_vector[int(a+b)]-i)/Width)
            region_map = union_find(i, j, Width, size_min, size_max, region_map, 0, 1, f1, f2_white)              #vizinho norte
            region_map = union_find(i, j, Width, size_min, size_max, region_map, 0, -1, f1, f2_white)             #vizinho sul
            region_map = union_find(i, j, Width, size_min, size_max, region_map, 1, 0, f1, f2_white)              #vizinho leste
            region_map = union_find(i, j, Width, size_min, size_max, region_map, -1, 0, f1, f2_white)             #vizinho oeste

        #print >> f2_white, "b = ", b
        print "b = ", b
        b = b + num_pix                                                         #incrementa valor b
        im3 = region_map[0,:,:]#visual
        cv2.imwrite("im_" + str(b) + ".bmp", im3)#visual
    f1.close()
    f2_white.close()
    pass

if __name__ == "__main__":
    main(sys.argv)
