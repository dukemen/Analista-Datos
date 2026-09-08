
def cargar_pdf(archivo):
    #cargamos el archivo
    pdf = PdfFileReader(open(archivo, "rb"))
    #obtenemos el numero de paginas
    num_paginas = pdf.getNumPages()
    #imprimimos el numero de paginas del pdf
    print ("Este archivo PDF tiene",num_paginas,"páginas.")

    #recorremos todas las páginas del PDF y las mostramos por pantalla
    for i in range(0,num_paginas):
        print ("Página",i+1)
        pagina = pdf.getPage(i)

        texto = pagina.extractText()

        print (texto)

        print ("\n")