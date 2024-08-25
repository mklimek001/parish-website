document.getElementById('preview-button').addEventListener('click', function(event) {
    event.preventDefault();
    
    var content = document.getElementById('new-post-content').value;
    var htmlContent = marked(content);
    
    var previewWindow = window.open("", "Podgląd", "width=800,height=600");
    previewWindow.document.open();
    previewWindow.document.write(`
        <html>
        <head>
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,300;0,400;0,700;1,400&display=swap" rel="stylesheet">
            <title>Podgląd</title>
            <style>
                body {
                    margin: 0;
                    padding: 16px;
                    color: #000;
                    font-family: 'Poppins', sans-serif;
                }

                img{
                    object-fit: scale-down;
                    width: 100%;
                }

                h1, h2, h3, h4, h5, h6 {
                    font-weight: 400;
                    margin: 5px 0 0;
                }

                h1{
                    margin: 24px 10px 16px;
                    font-size: 32px;
                }

                h2{
                    margin: 24px 10px 14px;
                    font-size: 28px;
                }

                h3{
                    font-size: 24px;
                    margin: 24px 10px 12px 10px;
                    margin-left: 10px;
                }

                h4{
                    font-size: 22px;
                    margin: 20px 10px 10px 10px;
                    font-weight: 400;
                }
            </style>
        </head>
        <body>
            ${htmlContent}
        </body>
        </html>
    `);
    previewWindow.document.close();
});
