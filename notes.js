// go to https://gameinformer.com/covers
// $0 = div class="covers-container"
x = $0.querySelectorAll("a.gallery")
Array.from(x).map(y => y.href)

// then need to post process the urls, make sure they all have the same path prefix before year or imagefeed
// then make sure ending is webp
// then some code to download them all, ignoring ones we downloaded already