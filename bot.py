import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from urllib.parse import urlparse
import random
import itertools

def initialiser_navigateur():
    """
    Initialise et retourne une instance du navigateur Chrome non détectable
    
    Returns:
        uc.Chrome: Instance du navigateur
    """
    options = uc.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-notifications')
    
    # Paramètres pour éviter la détection
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    
    # Ajoute des en-têtes personnalisés
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Initialise le navigateur avec undetected-chromedriver
    driver = uc.Chrome(options=options)
    
    # Configure le comportement du navigateur pour le rendre plus humain
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    # Ajoute des paramètres webdriver pour éviter la détection
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def attendre_aleatoire(min_secondes=1, max_secondes=3):
    """
    Attend un temps aléatoire pour simuler un comportement humain
    """
    time.sleep(random.uniform(min_secondes, max_secondes))

def simuler_frappe_humaine(element, texte):
    """
    Simule une frappe humaine avec des délais aléatoires
    """
    for caractere in texte:
        element.send_keys(caractere)
        attendre_aleatoire(0.1, 0.3)

def verifier_captcha(driver):
    """
    Vérifie la présence d'un CAPTCHA et attend si nécessaire
    
    Args:
        driver: Instance du navigateur
    """
    try:
        captcha_frame = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[title*='reCAPTCHA']"))
        )
        if captcha_frame:
            print("\n⚠️ CAPTCHA détecté! Attente de la résolution manuelle...")
            input("Appuyez sur Entrée une fois le CAPTCHA résolu pour continuer...")
            print("Reprise de la recherche...")
            attendre_aleatoire(2, 4)
    except:
        pass

def verifier_url(url):
    """
    Vérifie et corrige l'URL si nécessaire
    
    Args:
        url (str): L'URL à vérifier
    Returns:
        str: L'URL corrigée
    """
    # Ajoute http:// si aucun protocole n'est spécifié
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Vérifie si l'URL est valide
    try:
        result = urlparse(url)
        return url if all([result.scheme, result.netloc]) else None
    except:
        return None

def recherche_et_acces_site(driver, mots_clefs, site_cible, max_pages=5):
    """
    Recherche un site spécifique via Google et y accède
    
    Args:
        driver: Instance du navigateur
        mots_clefs (str): Les mots-clés pour la recherche
        site_cible (str): Le nom du site à trouver
        max_pages (int): Nombre maximum de pages à parcourir
    Returns:
        tuple: (bool, int) - (site trouvé, numéro de page où le site a été trouvé)
    """
    try:
        # Accède à Google avec un délai aléatoire
        driver.get("https://www.google.com")
        attendre_aleatoire(2, 4)
        
        # Gère la popup de consentement des cookies si elle apparaît
        try:
            accept_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Tout accepter')]"))
            )
            attendre_aleatoire(1, 2)
            accept_button.click()
            attendre_aleatoire(1, 2)
        except:
            print("Pas de popup de cookies ou impossible de la gérer")
        
        # Attend que la barre de recherche soit chargée et cliquable
        search_box = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "q"))
        )
        
        # Simule une frappe humaine pour les mots-clés
        simuler_frappe_humaine(search_box, mots_clefs)
        attendre_aleatoire(0.5, 1.5)
        search_box.send_keys(Keys.RETURN)
        
        # Parcourt les pages de résultats
        page_actuelle = 1
        site_trouve = False
        
        while page_actuelle <= max_pages and not site_trouve:
            print(f"\nRecherche dans la page {page_actuelle}...")
            attendre_aleatoire(2, 4)
            
            # Cherche tous les liens dans les résultats
            try:
                resultats = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.yuRUbf a"))
                )
                
                # Cherche le site cible dans les résultats
                for resultat in resultats:
                    url = resultat.get_attribute('href')
                    if site_cible.lower() in url.lower():
                        print(f"\nSite trouvé : {url}")
                        attendre_aleatoire(1, 2)
                        resultat.click()
                        site_trouve = True
                        return True, page_actuelle
                
                if not site_trouve and page_actuelle < max_pages:
                    try:
                        next_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.ID, "pnnext"))
                        )
                        attendre_aleatoire(1, 3)
                        next_button.click()
                        page_actuelle += 1
                    except:
                        print("Plus de pages suivantes disponibles")
                        break
                
            except Exception as e:
                print(f"Erreur lors de la recherche dans la page {page_actuelle}: {e}")
                break
        
        if not site_trouve:
            print(f"\nSite {site_cible} non trouvé après {page_actuelle} pages de recherche")
            return False, 0
        
        # Attend que la nouvelle page soit chargée
        attendre_aleatoire(3, 5)
        
    except Exception as e:
        print(f"Une erreur s'est produite: {e}")
        return False, 0

def generer_combinaisons_aleatoires(mots_clefs, taille_min=2, taille_max=None, max_combinaisons=10):
    """
    Génère un nombre limité de combinaisons pertinentes des mots-clés
    
    Args:
        mots_clefs (list): Liste des mots-clés
        taille_min (int): Taille minimale des combinaisons
        taille_max (int): Taille maximale des combinaisons
        max_combinaisons (int): Nombre maximum de combinaisons à générer
    Returns:
        list: Liste des combinaisons sélectionnées
    """
    if taille_max is None:
        taille_max = min(len(mots_clefs), 4)  # Limite à 4 mots maximum
    
    toutes_combinaisons = []
    for r in range(taille_min, taille_max + 1):
        combinaisons = list(itertools.combinations(mots_clefs, r))
        toutes_combinaisons.extend(combinaisons)
    
    # Mélange les combinaisons
    random.shuffle(toutes_combinaisons)
    
    # Limite le nombre de combinaisons
    return toutes_combinaisons[:max_combinaisons]

def main():
    # Initialise le navigateur une seule fois
    driver = initialiser_navigateur()
    
    try:
        while True:
            # Demande la liste des mots-clés
            mots_input = input("Entrez vos mots-clés séparés par des virgules : ")
            if mots_input.lower() == 'quit':
                break
                
            mots_clefs = [mot.strip() for mot in mots_input.split(',')]
            site_cible = input("Entrez le nom du site à trouver (ex: wikipedia.org) : ")
            max_pages = int(input("Nombre maximum de pages à parcourir (défaut: 5) : ") or "5")
            max_combinaisons = int(input("Nombre maximum de combinaisons à tester (défaut: 10) : ") or "10")
            
            # Génère les combinaisons avec les nouveaux paramètres
            combinaisons = generer_combinaisons_aleatoires(mots_clefs, taille_min=2, max_combinaisons=max_combinaisons)
            total_combinaisons = len(combinaisons)
            
            print(f"\nNombre total de combinaisons à tester : {total_combinaisons}")
            
            # Pour stocker les résultats
            resultats_recherche = []
            
            # Teste chaque combinaison
            for i, combo in enumerate(combinaisons, 1):
                mots_recherche = ' '.join(combo)
                print(f"\nTest de la combinaison {i}/{total_combinaisons} : {mots_recherche}")
                trouve, page = recherche_et_acces_site(driver, mots_recherche, site_cible, max_pages)
                if trouve:
                    resultats_recherche.append((combo, page))
                    # Si on trouve le site, on peut éventuellement arrêter ici
                    if input("\nSite trouvé ! Voulez-vous continuer avec d'autres combinaisons ? (oui/non) : ").lower() != 'oui':
                        break
                
                # Petite pause entre chaque recherche pour éviter de surcharger Google
                attendre_aleatoire(5, 8)
            
            # Affiche le résumé des résultats
            print("\n=== Résumé des recherches ===")
            if resultats_recherche:
                print("Combinaisons ayant trouvé le site :")
                for combo, page in resultats_recherche:
                    print(f"- Combinaison '{' '.join(combo)}' -> Trouvé à la page {page}")
            else:
                print("Aucune combinaison n'a permis de trouver le site.")
            
            print("\nToutes les combinaisons ont été testées!")
            continuer = input("\nVoulez-vous faire une autre recherche avec de nouveaux mots-clés ? (oui/non) : ")
            if continuer.lower() != 'oui':
                break
    
    finally:
        # Ferme le navigateur à la fin
        driver.quit()

if __name__ == "__main__":
    main()
