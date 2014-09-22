# server.R
library(ggplot2)
library(reshape2)
library(RCurl)
library(data.table)

shinyServer(function(input, output) {
  output$text <- renderText({
    for (i in input$country)
    {
      print(i)
    }
  })
  output$plots <- renderPlot({
    countrylist=c("sierra_leone","guinee","liberia")
    casefinal <- NA
    for (i in input$country)
    {
      file1 <- getURL(paste("https://raw.githubusercontent.com/InstituteforDiseaseModeling/EVD/master/",countrylist[strtoi(i)], "_EVD_2014.csv",sep=""))
      case1 <- read.csv(text = file1, stringsAsFactors = F)
      case1$X <- as.Date(case1$X, format="%m/%d/%Y")
    if (is.na(casefinal))
    {
      casefinal <- case1
    }
    else
    {
      casefinal <- merge(casefinal, case1, by="X")
    }
    }
    casefinal$Week <- week(casefinal$X)
    casefinal$Month <- month(casefinal$X)
    casefinal <- as.data.table(casefinal)
    if (input$aggregation==2)
    {
      casefinal <- casefinal[,lapply(.SD,sum,na.rm=TRUE),by = Week]
      casefinal$X <- casefinal$Week
    }
    else if (input$aggregation==3)
    {
      casefinal <- casefinal[,lapply(.SD,sum,na.rm=TRUE),by = Month]
      casefinal$X <- casefinal$Month
    }
    casefinal$Week <- NULL
    casefinal$Month <- NULL
    
    p <- ggplot(melt(casefinal, id.vars="X"),aes(x=X,y=value))+
      geom_line()+facet_wrap(~ variable) +
      xlab("Time") +
      ylab("Number of New Cases") + theme_bw()
    if (input$yscale==2)
      {
        p <- p + scale_y_log10()
      }
    p
  })
  }
  )