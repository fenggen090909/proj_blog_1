/*!
* Start Bootstrap - Clean Blog v6.0.9 (https://startbootstrap.com/theme/clean-blog)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-clean-blog/blob/master/LICENSE)
*/
window.addEventListener('DOMContentLoaded', () => {
    let scrollPos = 0;
    const mainNav = document.getElementById('mainNav');
    const headerHeight = mainNav.clientHeight;
    window.addEventListener('scroll', function() {
        const currentTop = document.body.getBoundingClientRect().top * -1;
        if ( currentTop < scrollPos) {
            // Scrolling Up
            if (currentTop > 0 && mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-visible');
            } else {
                console.log(123);
                mainNav.classList.remove('is-visible', 'is-fixed');
            }
        } else {
            // Scrolling Down
            mainNav.classList.remove(['is-visible']);
            if (currentTop > headerHeight && !mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-fixed');
            }
        }
        scrollPos = currentTop;
    });
})


const loadMoreButton = document.getElementById('load-more');
const newPostsContainer = document.getElementById('new-posts');
const postListContainer = document.getElementById('post-list');

let offset = 3; // 初始偏移量为 3，因为已经加载了 3 篇文章
const limit = 3; // 每次加载 10 篇文章

loadMoreButton.addEventListener('click', function(event) {
    event.preventDefault();

    fetch(`/load_more_posts?offset=${offset}&limit=${limit}`)
        .then(response => response.json())
        .then(data => {
            if (data.length > 0) { // 检查是否还有更多文章
                data.forEach(post => {
                    const postDiv = document.createElement('div');
                    postDiv.className = 'post-preview';
                    postDiv.innerHTML = `
                        <a href="post.html">
                            <h2 class="post-title">${post.title}</h2>
                            <h3 class="post-subtitle">sub_title</h3>
                        </a>
                        <p class="post-meta">
                            Posted by
                            <a href="#">Gen Feng</a>
                            on ${post.date_posted}
                        </p>
                    `;
                    newPostsContainer.appendChild(postDiv);
                    newPostsContainer.appendChild(document.createElement('hr'));
                });
                offset += data.length; // 更新偏移量
            } else {
                // 没有更多文章了，可以禁用按钮或显示提示信息
                loadMoreButton.disabled = true;
                loadMoreButton.textContent = "没有更多文章了";
            }
        });
});
