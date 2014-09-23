# server.R
library(ggplot2)
library(reshape2)
library(RCurl)
library(data.table)
library(maptools)

shinyServer(function(input, output) {
  output$text <- renderText({
    for (i in input$country)
    {
      print(i)
    }
  })
#   output$map <- renderPlot({
#     countrylist=c("sierra_leone","guinee","liberia")
#     for (i in input$country)
#     {
#       filelocation <- paste("https://raw.githubusercontent.com/InstituteforDiseaseModeling/EVD/master/",countrylist[strtoi(i)], "_shapefile.csv",sep="")
#       download.file(filelocation, "district.shp")
#       shapes<-readShapeSpatial("district.shp",
#                              proj4string=CRS("+proj=longlat"))
#     }
#   })
  output$plots <- renderPlot({
    countrylist=c("sierra_leone","guinee","liberia")
    casefinal <- NA
    for (i in input$country)
    {
      file1 <- getURL(paste("https://raw.githubusercontent.com/InstituteforDiseaseModeling/EVD/master/",countrylist[strtoi(i)], "_EVD_2014.csv",sep=""))
      case1 <- read.csv(text = file1, stringsAsFactors = F)
      case1$X <- as.Date(case1$X, format="%m/%d/%Y")
      filepop <- getURL(paste("https://raw.githubusercontent.com/InstituteforDiseaseModeling/EVD/master/",countrylist[strtoi(i)], "_population.csv",sep=""))
      pop <- read.csv(text = filepop, stringsAsFactors = F)
      

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
      casefinal$X <- as.POSIXct(paste("2014",casefinal$Week,"1"), format="%Y %U %u")
    }
    else if (input$aggregation==3)
    {
      casefinal <- casefinal[,lapply(.SD,sum,na.rm=TRUE),by = Month]
      casefinal$X <- as.POSIXct(paste("2014",casefinal$Month,"1"), format="%Y %m %d")
    }
    casefinal$Week <- NULL
    casefinal$Month <- NULL
    casefinal$CountryTotal <- rowSums(subset(casefinal,select=-X),na.rm=TRUE)
    p <- ggplot(melt(casefinal, id.vars="X"),aes(x=X,y=value))+
      geom_point(size = 1)+geom_line()+facet_wrap(~ variable,ncol = 4) +
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