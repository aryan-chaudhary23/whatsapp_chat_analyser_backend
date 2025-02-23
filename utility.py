import pandas as pd
from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib
import emoji
import seaborn as sns
matplotlib.use('Agg')  # Prevents using Tkinter for rendering
extractor=URLExtract()

def fetch_stats(selected_user,df):
    if selected_user!= "Whole Analysis":
        df=df[df['user']== selected_user]
    num_messges= df.shape[0] #1. found total number of messages
    words=[]
    for message in df['message']:
        words.extend(message.split()) #2. found total number of words used
    num_media_messages=df[df['message']=='<Media omitted>\n'].shape[0] #3. found number of media files sent
    #if we see our chats medai files are replaced by  media omiited also \n present ie. not visible but it is there
    links=[]
    for message in df['message']:
        links.extend(extractor.find_urls(message)) #4. found total links shared in our chat
    df = df[df['user'] != 'group_notification']
    df = df[~df['message'].isin(['<Media omitted>\n', 'This message was deleted\n'])]
    #5. drawing graph of the most active users and number of messages they sent only done if selected user is Whole Analysis
    active_user_img_link=None
    total_user_percen=None
    if selected_user=="Whole Analysis":
        x=df['user'].value_counts()
        print(type(x))
        name=x.head().index
        count=x.head().values
        plt.bar(name,count)
        plt.xticks(rotation='vertical')
        active_user_img_link='static/bar_plot.png'
        plt.savefig(active_user_img_link)
        plt.close()
        user_percent=round((df['user'].value_counts()/df.shape[0])*100,2)
        total_user_percen=list(user_percent.items())
    #6. drawing a wordcloud
    wordcloud_display=createWordCloud(selected_user,df)
    #7. seeing the top words used in out gc
    #but we also need to do some more preprocessing ie.
         #- remove group messages
         #- remove media ommited message
         #- remove stop words
    common_words=most_common_words(selected_user,df)
    plt.figure(figsize=(10,8))
    plt.barh(common_words[0],common_words[1],color='orange')
    common_words_link='static/bar_plot2.png'
    plt.xticks(rotation='vertical')
    plt.savefig(common_words_link)
    plt.close()
    #8. Doing emoji analysis
    all_emojis=all_emo(selected_user,df)
    print(all_emojis)
    plt.figure(figsize=(8,6))
    plt.pie(
        all_emojis[1].head(),
        labels=[str(emoji) for emoji in all_emojis[0].head()],
        autopct="%0.2f"
    )
    emoji_link='static.pie1.png'
    plt.savefig(emoji_link, dpi=300)
    plt.show()
    #print(type(all_emojis))
    all_emojis = tuple((row[0], int(row[1])) for row in all_emojis.head(20).itertuples(index=False))
    timeline_link=monthly_timeline(selected_user,df)
    daily_timeline_link=daily_timeline(selected_user,df)
    #need to print all emojis with their counts
    #also emojis not showing in javascript handle that
    weekly_timeline_link=weekly_timeline(selected_user,df)
    monthly_timeline_link=month_activity(selected_user,df)
    heatmap_link=heatmap(selected_user,df)
    return num_messges,words,num_media_messages,links,active_user_img_link,total_user_percen,wordcloud_display,common_words_link,emoji_link,all_emojis,timeline_link,daily_timeline_link,weekly_timeline_link,monthly_timeline_link,heatmap_link


def createWordCloud(selected_user, df):
    # If the selected user is "Whole Analysis", filter the dataframe
    if selected_user != "Whole Analysis":
        df = df[df['user'] == selected_user]
    # Generate the word cloud
    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    wc.generate(df['message'].str.cat(sep=" "))

    # Save the word cloud image to the static folder
    link = 'static/wordcloud.png'
    wc.to_file(link)  # Saves the word cloud image to the specified path

    # Return the link to the saved image
    return link

def most_common_words(selected_user,df):
    if selected_user != "Whole Analysis":
        df=df[df['user']==selected_user]
    f=open('stop_hinglish.txt','r')
    stop_words=f.read()
    words=[]
    for message in df['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)
    return_df=pd.DataFrame(Counter(words).most_common(20))
    return return_df

def all_emo(selected_user,df):
    if selected_user!="Whole Analysis":
        df=df[df['user']==selected_user]
    emojis=[]
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])
    emoji_df=pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    return emoji_df

def monthly_timeline(selected_user,df):
    if selected_user!="Whole Analysis":
        df=df[df['user']==selected_user]
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i])) #gives us July-2019,January-2020 so we can draw our bar graph
    timeline['time'] = time
    link='static/timeline.png'
    plt.figure(figsize=(12,12))
    plt.plot(timeline['time'],timeline['message'],color='green')
    plt.xticks(rotation='vertical')
    plt.savefig(link)
    plt.close()
    return link

def daily_timeline(selected_user,df):
    if selected_user!="Whole Analysis":
        df=df[df['user']==selected_user]
    daily_time=df.groupby('only_date').count()['message'].reset_index()
    link='static/timeline2.png'
    plt.figure(figsize=(12,10))
    plt.plot(daily_time['only_date'],daily_time['message'],color='blue')
    plt.xticks(rotation='vertical')
    plt.savefig(link)
    plt.close()
    return link

def weekly_timeline(selected_user,df):
    if selected_user!="Whole Analysis":
        df=df[df['user']==selected_user]
    busy_day=df['day_name'].value_counts()
    link='static/timeline3.png'
    plt.figure(figsize=(10,9))
    plt.bar(busy_day.index,busy_day.values,color='red')
    plt.xticks(rotation='vertical')
    plt.savefig(link)
    plt.close()
    return link

def month_activity(selected_user,df):
    if selected_user!="Whole Analysis":
        df=df[df['user']==selected_user]
    df=df['month'].value_counts()
    link='static/timeline4.png'
    plt.figure(figsize=(10, 9))
    plt.bar(df.index,df.values,color='green')
    plt.xticks(rotation='vertical')
    plt.savefig(link)
    plt.close()
    return link

def heatmap(selected_user,df):
    if selected_user!="Whole Analysis":
        df=df[df['user']==selected_user]
    user_heatmap=df.pivot_table(index='day_name',columns='period',values='message',aggfunc='count',fill_value=0)
    plt.figure(figsize=(10,8))
    sns.heatmap(user_heatmap)
    link='static/heatmap.png'
    plt.savefig(link)
    plt.close()
    return link

