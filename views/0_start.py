import streamlit as st
import feedparser

st.write('''
    # Das StonedLack Universum 🏈
''')

with st.expander("StonedLack News", icon=":material/news:", expanded=True):
    st.write('''             
    #### Der Montagspodcast ist zurück
    Seit dem 03.03.2025 sind die beiden Podcaster Stoni und Lack wieder live auf Sendung und präsentieren die üblichen Offseason-Themen. In der aktuellen Folge 497 wird die Free Agency behandelt.
             
    Die nächste Folge wird live am 10.03.2025 um 21:30 Uhr gestreamt.

    #### kunfc. ist der Champ of Champs 2024
    Mit dem Ausgang des Superbowls entschied sich auch die Frage, wer sich im Champ of Champs-Spiel durchsetzt. Letzlich ergattert sich kunfc. (sleeper: kunfc) den begehrten Titel und den Siegespreis.
    
    Das Champ of Champs-Spiel im Superbowl bestand aus der Auswahl von drei Spielern, deren Fantasy-Performances mit einem Faktor multipliziert wurde. Bester Fantasy Spieler der Runde war Worthy mit insgesamt 107,10 Fantasy Punkten (bei einem Faktor x3). 
    
    kunfc setzte auf Worthy, AJ Brown und Goedert und sammelte somit insgesamt 161,1 Fantasy Punkte, was die Verteidigung der Führung und den Gesamtsieg bedeutete. Glückwunsch zum Sieg und viel Spaß mit dem Preis.
    
    #### Aktuelle Podcast-Folgen
    - **#498 (10.03.2025)**
    - **#497 (03.03.2025):** Free Agency Wünsche 2025 ([Youtube](https://www.youtube.com/watch?v=BgWIwJSINXI))
    ''')

with st.expander("NFL News", icon=":material/news:"):
    # URL des Rotowire NFL RSS-Feeds
    RSS_FEED_URL = "https://www.rotowire.com/rss/news.php?sport=NFL"

    def get_news():
        feed = feedparser.parse(RSS_FEED_URL)
        return feed.entries  # Liste der News-Artikel
    news_entries = get_news()

    for entry in news_entries:
        st.write(f"#### {entry.title}")
        st.write(f"📰 {entry.published}")
        st.text(entry.summary)
        st.markdown(f"🔗 [Zum Artikel]({entry.link})", unsafe_allow_html=True)
        st.write("---")

with st.expander("About", icon=":material/question_mark:"):
    st.write(
        '''
    Willkommen auf der Streamlit-Infoseite des StonedLack Fantasy Football Podcasts. 
         
    _**Hinweis/Disclaimer:** Die Seite wird privat betrieben und dient nur dem Zwecke der Aufbereitung von frei zugänglichen Daten aus der sleeper-API ([Link](https://docs.sleeper.com/)).
    Die Seite steht in keiner Verbindung zu den Podcast-Autoren und wird als zusätzliches Angebot ("Fan-Page") betrieben._
    
    #### Stoned _what_ !?
    StonedLack ist ein Live-Podcast der beiden Fantasy Football-Heads **Stoni** und **Lack** aus Wien.
    Beinahe das ganze Jahr über betreiben sie den Podcast, der u. a. live auf dem [youtube-Kanal](https://www.youtube.com/@stonedlack) verfolgt werden kann.
    Der Podcast ist auch auf allen gängigen Streaming-Plattformen verfügbar.
    
    Um den Podcast hat sich mittlerweile eine große Gemeinde Fantasy Football-Begeisterter versammelt, die den Podcast verfolgt, selbst aktiv einbringt etc. pp.
    Fast aller Austausch in der Community findet auf dem Discord-Channel ([Einladungslink](https://discord.gg/V9pt9MZ6Ch)) statt.
         
    #### StonedLack Ligen
    Seit vielen Jahren organisieren StonedLack eigene Ligen, in denen die Zuschauenden und -hörenden gegeneinander antreten. 
    Jedes Jahr werden so bspw. Redraftligen organisiert, die dann live im Podcast ausgelost werden. 
         
    Des Weiteren gibt es viele Dynasty-Ligen, die über viele Jahre hinweg bespielt werden. 
         
    Die Gewinner jeder Liga spielen um die **'MaryoLarry Trophy'** und den Gesamtsieg.
         
    #### Schön und gut, aber was soll das hier?!
    Gute Frage. Ich höre den Podcast seit gut drei Jahren. 
    Um allen aus der Community einen Zugang zu den Redraftligen zu gewähren, habe ich vor 2 Jahren angefangen, die API der Plattform [sleeper](sleeper.com), 
    auf der die Ligen organisiert sind, auszulesen.
         
    Angefangen hat alles mit der Idee, ein ADP-Draftboard aus allen Ligen zu generieren, also ein Spielerranking über alle Drafts der 2023er-StonedLack Redraftligen zu erstellen.
    In der Folge habe ich begonnen, wöchentliche Updates zu allen Ligen in Discord zu schreiben. Motivation war auch, die Programmiersprache `python` besser kennen zu lernen.
         
    Nun mündet das Ganze in meinem vorerst größten und sichtbarstem Projekt, dieser Streamlit-Plattform. 
    Der Gedanke dahinter ist, für die kommende Fantasy-Saison eine Plattform zu bauen, in der man mehr Informationen bieten und darstellen kann,
    als in einer Discord-Nachricht. Daher ist die Seite auch noch ständigen Updates und Änderungen ausgesetzt.
         
    Wer Ideen und Wünsche hat, kann diese gern äußern und mir im Discord schreiben. Ihr wisst ja, wo Ihr mich finden könnt.😉
         
    Viel Spaß auf der Seite und bei Fantasy Football!
    ''')

with st.expander("The Universe", icon=":material/planet:"):
    st.write('''    
    Das Universum umfasste in der Saison 2024 über 60 Dynasty- und Redraftligen. Auf den folgenden Seiten findet ihr Einblicke zu den wöchentlichen Statistiken, Matchups, zu den Drafts etc.
    ''')
