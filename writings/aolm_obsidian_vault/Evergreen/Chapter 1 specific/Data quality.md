      

One challenge for [[qualitative interpretation of computational models of literature]] is the difficulty in ascertaining the quality of the underlying data set(s) from which those models are produced.

Data quality as a function of processes happening to a text [[over time]]
and changing the structure/characteristics of the data [[over time]]
  - each graph is the next stage in the [[text cleaning]] process

First idea - change in slope to word frequency vectors as a text is cleaned up
- in very discrete small steps
- slope is gradient field vector (each component is partial derivative with respect to its dimension - x,y,z, etc.

Next, determine [[information loss]]/likelihood function in order to perform model selection via information criteria

Could be understanding the difference in regression lines as new text frequency vectors are added with further cleanup
  - change in correlation between the vector (use PCA) and text time

Secondary idea - change in magnitude of vector over text time
  - each graph is the next stage in the text cleaning process

If you can quantify the information loss over time, we can get discrete measures of how much these changes will change further modeling down the line

Data quality becomes a function of [[text cleaning]] vs [[information loss]]
  - Some things like the header/footer may be excusable but maybe not more internal cleaning methods. For instance, removing stop words or lemmatizing may be too lossy.

**Heuristic for data quality exploration**

1. What is the slope of the line over time of the corpora word vector over text time as it develops
2. How does document cleaning, word cleaning, and stop word lists alter the slope of that line?
3. What are the repercussions down the line?
4. Can we measure the information loss of each of those processes?
5. Consider different apis/methods that perform the same function and notice if there is a difference across methods
6. Take notes on noticings as this exploration  and measurement is done
7. Start with a simple document from Project Gutenberg.
8. Figure out its sections and begin the process