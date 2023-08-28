# fl

My projects for freelance


1) # Parametrs

    -f or --filename - Set filename, where result will be save. default - result.txt
    
    -u or --url - Set url with filters on https://realtica.com. default - https://www.realitica.com/index.php?for=Prodaja&opa=Budva&type%5B%5D=&type%5B%5D=Apartment&price-min=30000&price-max=150000&since-day=p-anytime&qry=&lng=hr
    
    -d or --domain Set domain from url. default - https://realtica.com
    
    exemples: 
    1) python main.py
    2) python main.py -f res.txt
    3) pyton main.py --filename res.txt -url https://realtica.com... --domain https://realtica.com
    4) pyton main.py --f res.txt -u https://realtica.com... -d https://realtica.com