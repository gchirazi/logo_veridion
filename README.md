# #1 Logo Similarity
## The first challenge of the project is downloading the logos. 
While extracting them from the **\<head>** section of each website seems like the ideal approach, many of the sites in the list do not have their logo there. Therefore, using an **API** like the one I found from **Clearbit** proves to be the fastest and most universal solution.

## The second challenge is preprocessing.
Since the logos are very similar, differing mainly in quality, **resizing** them to a low resolution, such as 32x32, becomes the most effective solution. Additionally, converting them to **grayscale** provides a good balance between speed and accuracy.

## The final and most important challenge is clustering.
After testing multiple algorithms, I found that **DBSCAN** often produces false positives, while **K-Means** is not a universal solution because it requires specifying the number of clusters, which is unknown in advance. Instead, **HDBSCAN** turned out to be the best option. It does not require specifying the number of clusters or an epsilon value, and its high-density principle aligns well with the nature of logo design. To correctly assign the logos that **HDBSCAN** initially disregards, we perform a reclustering based on **SSIM**, with a **threshold** of 0.8 determined through extensive testing.

Instead of a hard to read **CSV** preview, I opted for the quick generation of an **HTML** file to check the clusters. This file is simple, with no additional styling, displaying only the cluster number and the associated logos. This makes algorithm validation extremely easy and significantly improves the efficiency of the verification process.

## Results:  

To go through all the steps, I only uploaded the **main script**, `main.py`, and the Parquet file available on the Veridion website. When executed, all the previously mentioned processes will run automatically, and the **preview will be available** in `/cluster_reports` upon completion.  

I chose this approach to keep the script as **universal** as possible rather than hardcoding it, making it **adaptable** to any other set of websites.  

Since some logos are extremely similar or have differences that are barely noticeable even to the human eye, occasional misclassifications still occur. Despite this, I estimate the **current accuracy** to be around 90-95%. The results can be easily reviewed through the generated HTML file.
