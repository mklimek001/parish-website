const titleField = document.getElementById('title-field')
const contentField = document.getElementById('content-field')
const photoField = document.getElementById('photo-field')

var newsTitle = ""
var newsImgLink = ""
var newsContent = ""

var loadPosts = function(){
    fetch('posts.json')
    .then(function(response){
        return response.json();
    })
    .then(function (data){
        for(var i = data.posts.length-1; i >= 0; i--){
            document.getElementById('posts-row').innerHTML += '<div class="col-xl-3 col-md-5 col-sm-12 widget-box" >' +
            '<a href="singleinfo.html">' +
                '<div class="widget-inner-container" onclick=saveDetails('+ data.posts[i].ID +')>' + 
                    '<h2>' + data.posts[i].title  + '</h2>' +
                    '<img src="' +  data.posts[i].photo + '" alt="NewsImage">' +
                    '<p>' + data.posts[i].text.split(" ",11).join([separator = ' ']) + "..." + '</p>' +
                '</div>' +
            '</a>' +
        '</div>'
        }   
    })
    .catch(function (err){
        console.log(err);
    })
}


var saveDetails = function(postID) {
    console.log(postID);   
    localStorage.setItem('PostID',postID);   
}

var loadDetails = function() {
    var postID = localStorage.getItem('PostID');

    setTimeout(() => { fetch('posts.json')
        .then(function(response){
            return response.json();
        })
        .then(function (data){
            for(var i = data.posts.length-1; i >= 0; i--){
                if(postID == data.posts[i].ID){
                    newsTitle = data.posts[i].title;
                    newsImgLink = data.posts[i].photo;
                    newsContent = data.posts[i].text;

                    titleField.innerHTML = newsTitle;
                    contentField.innerHTML = newsContent; 
                    photoField.innerHTML =  '<img class="main-photo" src="' + newsImgLink + '" alt="NewsImage"></img>'
                }
            }

            threeLatest(postID);   
        })
        .catch(function (err){
            console.log(err);
    }) }, 50);
}

var threeLatest = function(currShowedID){
    console.log(currShowedID)
    
    fetch('posts.json')
        .then(function(response){
            return response.json();
        })
        .then(function (data){
            var choosenCounter = 0;
            var i = data.posts.length-1;

            while(choosenCounter < 3){
                if(data.posts[i].ID != currShowedID){
                    document.getElementById('three-posts-row').innerHTML += '<div class="col-xl-3 col-md-5 col-sm-12 widget-box" >' +
                        '<a href="singleinfo.html">' +
                            '<div class="widget-inner-container" onclick=saveDetails('+ data.posts[i].ID +')>' + 
                                '<h2>' + data.posts[i].title  + '</h2>' +
                                '<img src="' +  data.posts[i].photo + '" alt="NewsImage">' +
                                '<p>' + data.posts[i].text.split(" ",12).join([separator = ' ']) + "..." + '</p>' +
                            '</div>' +
                        '</a>' +
                    '</div>'
                    choosenCounter++;
                }
                i--;
            }   
        })
        .catch(function (err){
            console.log(err);
        })
}

