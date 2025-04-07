# visualizer.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pyLDAvis
import pyLDAvis.gensim_models as gensimvis

def plot_topic_trends(df, lda_model, hashtag):
    # Convert Timestamp to datetime and extract date
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Date'] = df['Timestamp'].dt.date
    
    # Group by date and topic to count occurrences
    trend_data = df.groupby(['Date', 'Dominant_Topic']).size().unstack(fill_value=0)
    
    # Extract topic names from LDA model
    topic_names = {}
    for topic_id in trend_data.columns:
        if topic_id != -1:  # Skip outlier topic (-1)
            topic_words = lda_model.show_topic(topic_id, topn=3)  # Get top 3 words
            topic_name = " ".join([word for word, _ in topic_words])  # Concatenate top words
            topic_names[topic_id] = f"Topic {topic_id + 1}: {topic_name}"
        else:
            topic_names[topic_id] = "Outliers"
    
    # Create plot
    plt.figure(figsize=(12, 6))
    for topic_id in trend_data.columns:
        if topic_id in topic_names:
            plt.plot(trend_data.index, trend_data[topic_id], label=topic_names[topic_id], marker='o')
    
    plt.title(f"Topic Trends Over Time for #{hashtag}")
    plt.xlabel("Date")
    plt.ylabel("Number of Tweets")
    plt.legend(title="Topics", bbox_to_anchor=(1.05, 1), loc='upper left')  # Move legend outside
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{hashtag}_topic_trends.png")
    plt.show()
    print(f"✅ Trend plot saved as {hashtag}_topic_trends.png")

def visualize_lda(lda_model, corpus, dictionary, hashtag):
    if lda_model and corpus and dictionary:
        vis_data = gensimvis.prepare(lda_model, corpus, dictionary)
        pyLDAvis.save_html(vis_data, f"{hashtag}_lda_visualization.html")
        print(f"✅ Interactive LDA visualization saved as {hashtag}_lda_visualization.html")
    else:
        print("Visualization failed: Missing model, corpus, or dictionary.")

if __name__ == "__main__":
    input_file = input("Enter the CSV file with topics (e.g., AI_tweets_processed_with_topics.csv): ").strip()
    hashtag = input("Enter the hashtag (without #): ").strip()
    df = pd.read_csv(input_file)
    # Note: For standalone testing, you'd need to load the LDA model separately
    plot_topic_trends(df, None, hashtag)  # Pass None if testing standalone