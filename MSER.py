import cv2
import numpy as np
import sys

def get_coordinate(position, Width): #GRADE COMECA NA POSICAO X=1 Y=1
    "Returns x and y positions for a given position, returns a list"
    i = int(position%Width)
    j = int((position-i)/Width)
    x_and_y  = [i, j]
    return x_and_y

def union_find(i, j, Width, size_min, size_max, region_map, seed_list, seed_list_filtered, absorb, x, y, f1, f2):
    "Runs the union_find algorithm (in progress)"
    try:
        region_map[0, j+y, i+x]
    except IndexError:
        #print >> f2, "vizinho nao existe"
        return region_map, seed_list_filtered, seed_list, absorb

    if (not(region_map[1, j, i])):  #cria link se nao foi visitado ainda
        region_map[3, j, i] = Width*j+i

    if (not(region_map[0, j+y, i+x]) or (region_map[0, j+y, i+x]==130)):   #se vizinho existe
    #if (region_map[0, j+y, i+x]):   #se vizinho existe
        # print >> f2, "vizinho existe", ",vizinho = ", region_map[0, j+y, i+x]
        # print >> f2, "atual:  i = ", i, "  j = ", j
        if (region_map[1, j+y, i+x]):    #se vizinho jah foi visitado
            #print >> f1, "vizinho foi visitado", ",visitado:",region_map[1, j+y, i+x] != 0
            if (region_map[1, j, i]):     #se pixel atual tem seed:
                #print >> f2, "MERGE"
                #print "viz visitado e px c seed"
                #print >> f2, "vizinho foi visitado e px atual tem seed (REGION MERGE)", "seed atual:", region_map[2, j, i]
                if (region_map[2, j, i] <= 0):
                    #print >> f2, "Atual nao eh o seed, Seed = ", region_map[2, j, i]
                    i_seed = i
                    j_seed = j
                else:
                    #print >> f2, "Atual nao eh o seed, Seed = ", region_map[2, j, i]
                    i_seed = get_coordinate(region_map[2, j, i], Width)[0]
                    j_seed = get_coordinate(region_map[2, j, i], Width)[1]
                if (region_map[2, j+y, i+x] <= 0):
                    #print >> f2, "Vizinho eh o seed, Seed = ", region_map[2, j+y, i+x]
                    i_seed_viz = i + x
                    j_seed_viz = j + y
                else:
                    #print >> f2, "Vizinho nao eh o seed, Seed = ", region_map[2, j+y, i+x]
                    i_seed_viz = get_coordinate(region_map[2, j+y, i+x], Width)[0]
                    j_seed_viz = get_coordinate(region_map[2, j+y, i+x], Width)[1]
                if ((i_seed == i_seed_viz) and (j_seed == j_seed_viz)):         #checa se pixel jah nao pertence a essa regiao
                   #print >> f2, "jah pertence a regiao"
                    region_map[1, j, i] = 1                                                                                                 #marca px atual como visitado
                    i_seed = get_coordinate(region_map[2, j, i], Width)[0]
                    j_seed = get_coordinate(region_map[2, j, i], Width)[1]
                    return region_map, seed_list_filtered, seed_list, absorb
                if (region_map[2, j_seed, i_seed] >= region_map[2, j_seed_viz, i_seed_viz]):#se seed da regiao atual menor ou igual regiao vizinha:
                    #print >> f2, "regiao atual some", region_map[2, j_seed, i_seed], ">=", region_map[2, j_seed_viz, i_seed_viz]
                    region_map[2, j_seed_viz, i_seed_viz] = region_map[2, j_seed, i_seed] + region_map[2, j_seed_viz, i_seed_viz] -1        #tamanho regiao vizinha atualizado
                    valor = region_map[3, j_seed, i_seed]
                    seed_list[Width*j_seed_viz+i_seed_viz] = region_map[2, j_seed_viz, i_seed_viz] #update regiao mantida
                    #print region_map[2, j_seed, i_seed]
                    #print region_map[2, j_seed_viz, i_seed_viz]
                    try:
                        del seed_list[Width*j_seed+i_seed] #deleta entrada antiga
                    except KeyError:
                        pass
                    for num_elem in xrange(1-int(region_map[2, j_seed, i_seed])):                                                           #loop que muda a seed de todos os px da regiao sendo eliminada
                        i_temp = get_coordinate(valor, Width)[0]
                        j_temp = get_coordinate(valor, Width)[1]
                        region_map[2, j_temp, i_temp] = Width*j_seed_viz+i_seed_viz
                        valor = region_map[3, j_temp, i_temp]
                else:   #se seed da regiao atual maior q regiao vizinha:
                    #print >> f2, "regiao vizinha some", region_map[2, j_seed, i_seed], "<", region_map[2, j_seed_viz, i_seed_viz]
                    region_map[2, j_seed, i_seed] = region_map[2, j_seed, i_seed] + region_map[2, j_seed_viz, i_seed_viz] -1                #tamanho regiao atual atualizado
                    valor = region_map[3, j_seed_viz, i_seed_viz]
                    seed_list[Width*j_seed+i_seed] = region_map[2, j_seed, i_seed] #update regiao mantida
                    try:
                        del seed_list[Width*j_seed_viz+i_seed_viz] #deleta entrada antiga
                    except KeyError:
                        pass
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
                #print "viz visitado e px s seed"
                #print >> f2, "vizinho foi visitado e px atual sem seed"
                if (region_map[2, j+y, i+x] <= 0): #testa se vizinho eh seed
                    #print >> f2, "Vizinho eh o seed, Seed = ", region_map[2, j+y, i+x]
                    i_seed_viz = i + x
                    j_seed_viz = j + y
                else:
                    #print >> f2, "Vizinho nao eh o seed, Seed = ", region_map[2, j+y, i+x]
                    i_seed_viz = get_coordinate(region_map[2, j+y, i+x], Width)[0]
                    j_seed_viz = get_coordinate(region_map[2, j+y, i+x], Width)[1]
                region_map[2, j, i] = int(Width*(j_seed_viz)+i_seed_viz)                                                                    #px atual se une a regiao vizinha
                region_map[2, j_seed_viz, i_seed_viz] = region_map[2, j_seed_viz, i_seed_viz] - 1                                           #atualiza U do seed de regiao vizinha
                seed_list[int(region_map[2, j, i])] = region_map[2, j_seed_viz, i_seed_viz]
                #print region_map[2, j, i]
                region_map[3, j, i] = region_map[3, j_seed_viz, i_seed_viz]                                                                 #px atual recebe link do seed de regiao vizinha
                region_map[3, j_seed_viz, i_seed_viz] = int(Width*(j)+i)                                                                    #seed de regiao vizinha recebe link de px atual
        else:   #se vizinho nao foi visitado:
            region_map[3, j+y, i+x] = Width*(j+y)+i+x#cria link do vizinho nao visitado
            #print >> f2, "vizinho nao foi visitado"
            if (region_map[2, j, i] == 0):  #se pixel atual nao tem seed:
                #print "viz n visitado e px sem seed"
                #print >> f2, "vizinho nao foi visitado e px atual sem seed", region_map[2, j, i]
                region_map[2, j+y, i+x] = int(Width*j+i)                                                                                    #cria regiao e adiciona vizinho(pixel atual vira Seed)
                #print >> f2, "criou seed"
                #seed_list_filtered = seed_list_filtered +1
                seed_list[int(region_map[2, j+y, i+x])] = region_map[2, j, i] =  - 1                                                                      #cria U da Seed da regiao atual
                region_map[3, j+y, i+x] = int(Width*j+i)                                                                                    #vizinho recebe link para px atual
                region_map[3, j, i] = int(Width*(j+y)+i+x)                                                                                  #px atual recebe link para px vizinho
            else:   #se px atual tem seed:
                #print >> f2, "vizinho nao foi visitado e px atual com seed", region_map[2, j, i]
                #print "viz n visitado mas px com seed"
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
    # try:
    #     seed_list[Width*j+i]
    # except KeyError:
    #     #seed_list_filtered = seed_list_filtered +1
    #     seed_list[Width*j+i] = 0
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
    if ((1-int(region_map[2, j_teste, i_teste]) >= size_min) and ((1-int(region_map[2, j_teste, i_teste]) < size_max))):
        absorb = region_map[3, :, :]
        for num_elem in xrange(1-int(region_map[2, j_teste, i_teste])):                                                       #loop que muda a seed de todos os px da regiao sendo eliminada
            i_temp = get_coordinate(valor, Width)[0]
            j_temp = get_coordinate(valor, Width)[1]
            valor = region_map[3, j_temp, i_temp]
            region_map[0, j_temp, i_temp] = 130
    count = 0
    change_flag = 0
    for key, value in seed_list.iteritems():
        if (((1-value) >= size_min) and ((1-value) < size_max)):
            seed_list_filtered[key] = value
            #print >> f2, seed_list_filtered
            change_flag = 1
    if change_flag == 1:
        for key, value in seed_list_filtered.iteritems():
            count = count + 1
        #print >> f2, count
    return region_map, seed_list_filtered, seed_list, absorb


def growth_rate(Q_prev, Q_curr, Q_fut, Max_stable):
    "Calculates maximun acceptable growth rate"
    for key, value in Q_curr.iteritems():
        try:
            a = Q_prev[key]
        except KeyError:
            return Max_stable
        try:
            b = Q_fut[key]
        except KeyError:
            return Max_stable
        if (float(((1-b)-(1-a))/Q_curr[key]) <= 0.5):
            Max_stable[key] = Q_curr[key]
    return Max_stable

def paint_max_stable(Max_stable,region_map, absorb, Width):
    "paints max stable region"
    for key, value in Max_stable.iteritems():
        i_teste = get_coordinate(key, Width)[0]
        j_teste = get_coordinate(key, Width)[1]
        valor = absorb[j_teste, i_teste]
        for num_elem in xrange(1-int(region_map[2, j_teste, i_teste])):                                                       #loop que muda a seed de todos os px da regiao sendo eliminada
            i_temp = get_coordinate(valor, Width)[0]
            j_temp = get_coordinate(valor, Width)[1]
            valor = absorb[j_temp, i_temp]
            region_map[0, j_temp, i_temp] = 130

def main(argv):
    image_name = "tiger"
    im = cv2.imread(str(image_name)+".bmp")

    f1 = open('f1', 'w+')
    f2 = open('f2', 'w+')
    Height = 240
    Width = 320
    # Height = 2560
    # Width = 3840
    # Height = 736
    # Width = 736

    size_min = 121
    size_max = 8500
    # size_min = 121
    # size_max = 123

    seed_list = {} #na vdd eh um dicionario

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


    cv2.imwrite(str(image_name)+"_bw.bmp", im)                                         #cria o bmp em grayscale

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
    seed_list_filtered = {}
    Max_stable = {}
    Q_curr = {}
    absorb = []
    for i in xrange(Width):
        for j in xrange(Height):
            region_map[0,j,i] = 255
    for num_pix in histogram:                                                   #itera pelas intensidades
        for a in xrange(int(num_pix)):                                          #marca pixeis dessa intensidade na camada visivel (PX)
            i = int(position_vector[int(a+b)]%Width)
            j = int((position_vector[int(a+b)]-i)/Width)
            region_map[0, j, i] = 0
            #region_map[0, j, i] = 255
            soma_pix_add.append(num_pix)
        #checa se encontra regioes ja criadas
        Q_prev = Q_curr
        Q_curr = seed_list_filtered
        for a in xrange(int(num_pix)):                                          #itera pelos pixeis adicionados nessa intensidade
            i = int(position_vector[int(a+b)]%Width)
            j = int((position_vector[int(a+b)]-i)/Width)
            region_map, seed_list_filtered, seed_list, absorb = union_find(i, j, Width, size_min, size_max, region_map, seed_list, seed_list_filtered, absorb, 0, 1, f1, f2)              #vizinho norte
            region_map, seed_list_filtered, seed_list, absorb = union_find(i, j, Width, size_min, size_max, region_map, seed_list, seed_list_filtered, absorb,0, -1, f1, f2)             #vizinho sul
            region_map, seed_list_filtered, seed_list, absorb = union_find(i, j, Width, size_min, size_max, region_map, seed_list, seed_list_filtered, absorb,1, 0, f1, f2)              #vizinho leste
            region_map, seed_list_filtered, seed_list, absorb = union_find(i, j, Width, size_min, size_max, region_map, seed_list, seed_list_filtered, absorb,-1, 0, f1, f2)             #vizinho oeste

        Q_fut = seed_list_filtered

        #Max_stable = growth_rate(Q_prev, Q_curr, Q_fut, Max_stable)
        #print >> f2, Max_stable

        #print >> f2, "b = ", b

        print "b = ", b
        b = b + num_pix                                                         #incrementa valor b
        #print >> f1, seed_list
        # if (b == Height*Width):
        im3 = region_map[0,:,:]#visual
        cv2.imwrite("im_" +str(b) + ".bmp", im3)#visual
        #     print >> f2, seed_list_filtered
    #paint_max_stable(Max_stable,region_map, absorb, Width)
    im3 = region_map[0,:,:]
    cv2.imwrite("im_" +str(image_name) + ".bmp", im3)
    f1.close()
    f2.close()
    pass

if __name__ == "__main__":
    main(sys.argv)




#PROBLEMA TA EM SINCRONIZAR AS OPERACOES DE PINTAR A IMAGEM COM VERIFICAR. TBM NAO FOI CONSIDERADO POR QUANTO TEMPO UMA REGIAO TEM QUE SER ESTAVEL PARA SER CONSIDERADA
