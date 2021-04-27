window.onload = () => {
    $('.ui.dropdown')
        .dropdown();
}

let special_wrapper

function initGoogleAuth(clientId = '1046681300300-2sh30nts0u505ustbjdso43p5gaaph7t.apps.googleusercontent.com') {
    gapi.auth2.init({
        client_id: clientId,
        scope: 'https://www.googleapis.com/auth/userinfo.email'
    }).then((data) => {
    }).catch(err => {
        console.log(err);
    });
}

function getCookie(key) {
    let cookie = document.cookie
    for (let e of cookie.split(';')) {
        let data = e.split('=')
        if (data[0].trim() === key) {
            return data[1]
        }
    }
    return null
}

function getIdToken() {
    try {
        let data = getCookie('token')
        if (data !== null) {
            return data
        }
        let user = gapi.auth2.getAuthInstance().currentUser.get();
        return user.getAuthResponse().id_token
    } catch {
        return null
    }
}

function getEmail() {
    try {
        let data = getCookie('email')
        if (data !== null) {
            return data
        }
        let user = gapi.auth2.getAuthInstance().currentUser.get();
        return user.getBasicProfile().getEmail()
    } catch {
        return null
    }
}

function getName() {
    try {
        let data = getCookie('name')
        if (data !== null) {
            return decodeURIComponent(data)
        }
        let user = gapi.auth2.getAuthInstance().currentUser.get();
        return user.getBasicProfile().getName()
    } catch {
        return null
    }
}

function isGoogleSignedIn() {

    let data = getCookie('token')
    if (data !== null) {
        return true
    }
    return gapi.auth2.getAuthInstance().isSignedIn.get()
}

async function getSpecialMenu(dates) {
    let param = dates.map((e) => {
        return `date=${e.month}:${e.day}`
    }).join('&')

    let res

    await axios.get('/api/v1/menu?' + param)
        .then((response) => {
            res = response
        });

    return res
}

async function getPermanentMenu() {
    let res
    await axios.get('/api/v1/menu/permanent')
        .then((response) => {
            res = response
        });

    return res
}

function dateToStruct(date) {
    date = new Date(date)
    return {month: date.getMonth() + 1, day: date.getDate()}
}

function dateOffset(day) {
    let date = new Date()
    date.setDate(date.getDate() + day)
    return date
}

const requestAnimationFrame = window.requestAnimationFrame ||
    window.mozRequestAnimationFrame ||
    window.webkitRequestAnimationFrame ||
    window.msRequestAnimationFrame;
window.requestAnimationFrame = requestAnimationFrame;


function easeOutQuart(from, to, now, duration) {
    return (1 - Math.pow((1 - (now / duration)), 4)) * (to - from) + from
}

Vue.component('special-menus', {
    template: `
           <div class="orange card special-container">
            <div class="content">
               <h2 class="ui header special-container-header">
                  <img src="/static/images/gyoza.svg" class="ui image special-container-header-image">
                  <p>日替わりメニュー</p>
               </h2>
            </div>
            
            <div id="special-wrapper">
            
            <div class="menu-vertical-wrapper">
                <div class="ui card">
                    <div class="image flag">
                        <img src="/static/images/finish-line.svg">
                    </div>
                    <div class="content">
                        これ以上アイテムはないようです
                    </div>
                </div>
            </div>
            <div class="menu-vertical-wrapper" v-for="special in specialMenus">
            <div><a class="ui orange tag label">{{ special.month }}月{{ special.day }}日 ({{ '日月火水木金土'[(new Date((new Date()).getFullYear(), special.month-1, special.day )).getDay()] }})</a></div>
                <div class="menu-card ui card" v-bind:class="{disabled: special.a_menu.is_sold_out && special.isToday}">
                    <header class="content">
                        <h2 class="ui header">
                            <div class="menu-name">
                                  <span class="header">
                                  <template v-if="special.isToday">
                                      <i class="teal check icon hit-area" v-if="!special.a_menu.is_sold_out" v-on:click="setSoldOut(special.a_menu.id, true, special.a_menu.name)"></i>
                                      <i class="red close icon hit-area" v-if="special.a_menu.is_sold_out" v-on:click="setSoldOut(special.a_menu.id, false, special.a_menu.name)"></i>
                                  </template>
                                  <span v-bind:class="{'header-text': special.isToday}">{{ special.a_menu.name }}</span>
                                  </span>
                            </div>
                            <div class="sub header flex-row" v-bind:class="{blurred: special.a_menu.is_sold_out && special.isToday}">
                                <div>Aメニュー<br>¥{{ special.a_menu.price }}<br></div>
                                <div class="ui right aligned">
                                <div class="ui left labeled button">
                                  <a class="ui basic right pointing label">
                                    {{ special.a_menu.like_count }}
                                  </a>
                                  <div class="ui red button" v-if="special.a_menu.is_liked" v-on:click="likeThis(special.a_menu, false)">
                                    <i class="heart icon"></i> スキ
                                  </div>
                                  <div class="ui button" v-else v-on:click="likeThis(special.a_menu, true)">
                                    <i class="heart icon"></i> スキ
                                  </div>
                                </div>
                                </div>
                            </div>
                        </h2>
                    </header>
                    <div class="image" v-bind:class="{blurred: special.a_menu.is_sold_out && special.isToday}">
                        <img v-bind:src='"http://placehold.jp/50/3d4070/ffffff/1280x960.jpg?text=http%3A%2F%2Flocalhost%3A8080%2Fstatic%2Fimage%2F%0A"+special.a_menu.id+".jpg%0A%20("+special.a_menu.name+")"' alt="Placeholder image" class="card-image">
                    </div>
                    <div class="content" v-bind:class="{blurred: special.a_menu.is_sold_out && special.isToday}">
                        <table>
                          <thead>
                            <tr><th>栄養</th>
                            <th>相当量</th>
                          </tr></thead>
                          <tbody>
                            <tr>
                              <td>
                                <h4 class="ui image header">
                                  <div class="content">
                                    エネルギー
                                    <div class="sub header">700 kcal
                                  </div>
                                </div>
                              </h4></td>
                              <td>
                                {{ special.a_menu.nutrition.energy }} kcal
                              </td>
                            </tr>
                            <tr>
                              <td>
                                <h4 class="ui header">
                                  <div class="content">
                                    タンパク質
                                    <div class="sub header">48 g
                                  </div>
                                </div>
                              </h4></td>
                              <td>
                                {{ special.a_menu.nutrition.protein }} g
                              </td>
                            </tr>
                            <tr>
                              <td>
                                <h4 class="ui header">
                                  <div class="content">
                                    脂質
                                    <div class="sub header">17 g
                                  </div>
                                </div>
                              </h4></td>
                              <td>
                                {{ special.a_menu.nutrition.fat }} g
                              </td>
                            </tr>
                            <tr>
                              <td>
                                <h4 class="ui header">
                                  <div class="content">
                                    塩分
                                    <div class="sub header">2.7 g
                                  </div>
                                </div>
                              </h4></td>
                              <td>
                                {{ special.a_menu.nutrition.salt }} g
                              </td>
                            </tr>
                          </tbody>
                        </table>
                    </div>
                </div>
                <div class="menu-card ui card" v-bind:class="{disabled: special.b_menu.is_sold_out && special.isToday }">
                    <header class="content">
                       <h2 class="ui header">
                            <div class="menu-name">
                                  <span class="header">
                                  <template v-if="special.isToday">
                                      <i class="teal check icon hit-area" v-if="!special.b_menu.is_sold_out" v-on:click="setSoldOut(special.b_menu.id, true, special.b_menu.name)"></i>
                                      <i class="red close icon hit-area" v-if="special.b_menu.is_sold_out" v-on:click="setSoldOut(special.b_menu.id, false, special.b_menu.name)"></i>
                                  </template>
                                  <span v-bind:class="{'header-text': special.isToday}">{{ special.b_menu.name }}</span>
                                  </span>
                            </div>
                            <div class="sub header flex-row">
                                <div>Bメニュー<br>¥{{ special.b_menu.price }}<br></div>
                                <div class="ui right aligned">
                                <div class="ui left labeled button">
                                  <a class="ui basic right pointing label">
                                    {{ special.b_menu.like_count }}
                                  </a>
                                  <div class="ui red button" v-if="special.b_menu.is_liked" v-on:click="likeThis(special.b_menu, false)">
                                    <i class="heart icon"></i> スキ
                                  </div>
                                  <div class="ui button" v-else v-on:click="likeThis(special.b_menu, true)">
                                    <i class="heart icon"></i> スキ
                                  </div>
                                </div>
                                </div>
                            </div>
                        </h2>
                    </header>
                    <div class="image">
                        <img v-bind:src='"http://placehold.jp/50/3d4070/ffffff/1280x960.jpg?text=http%3A%2F%2Flocalhost%3A8080%2Fstatic%2Fimage%2F%0A"+special.b_menu.id+".jpg%0A%20("+special.b_menu.name+")"' alt="Placeholder image" class="card-image">
                    </div>
                    <div class="content">
                        <table>
                          <thead>
                            <tr><th>栄養</th>
                            <th>相当量</th>
                          </tr></thead>
                          <tbody>
                            <tr>
                              <td>
                                <h4 class="ui image header">
                                  <div class="content">
                                    エネルギー
                                    <div class="sub header">700 kcal
                                  </div>
                                </div>
                              </h4></td>
                              <td>
                                {{ special.b_menu.nutrition.energy }} kcal
                              </td>
                            </tr>
                            <tr>
                              <td>
                                <h4 class="ui header">
                                  <div class="content">
                                    タンパク質
                                    <div class="sub header">48 g
                                  </div>
                                </div>
                              </h4></td>
                              <td>
                                {{ special.b_menu.nutrition.protein }} g
                              </td>
                            </tr>
                            <tr>
                              <td>
                                <h4 class="ui header">
                                  <div class="content">
                                    脂質
                                    <div class="sub header">17 g
                                  </div>
                                </div>
                              </h4></td>
                              <td>
                                {{ special.b_menu.nutrition.fat }} g
                              </td>
                            </tr>
                            <tr>
                              <td>
                                <h4 class="ui header">
                                  <div class="content">
                                    塩分
                                    <div class="sub header">2.7 g
                                  </div>
                                </div>
                              </h4></td>
                              <td>
                                {{ special.b_menu.nutrition.salt }} g
                              </td>
                            </tr>
                          </tbody>
                        </table>
                    </div>
                </div>
            </div>
            <div class="menu-vertical-wrapper">
                <div class="ui card">
                    <div class="image flag">
                        <img src="/static/images/finish-line.svg">
                    </div>
                    <div class="content">
                        これ以上アイテムはないようです
                    </div>
                </div>
            </div>
        </div>
</div>`,
    mounted: async function () {
        let today = new Date()
        let dates = []
        for (let i = 0; dates.length < 3; i++) {
            let date = dateOffset(i)
            if (date.getDay() !== 0 && date.getDay() !== 6) {
                dates.push(dateToStruct(date))
            }
        }
        for (let i = -1; dates.length < 5; i--) {
            let date = dateOffset(i)
            if (date.getDay() !== 0 && date.getDay() !== 6) {
                dates.push(dateToStruct(date))
            }
        }
        let result = await getSpecialMenu(dates)
        let data = result.data.schedules
        data.today = []
        for (let schedule of data) {
            if (schedule.month === today.getMonth() + 1 && schedule.day === today.getDate()) {
                schedule.isToday = true
                data.today = [schedule.a_menu, schedule.b_menu]
            } else {
                schedule.isToday = false
            }
        }
        this.setSpecial(data)
        this.specialMenus = data
    },
    updated: function () {
        special_wrapper = document.getElementById('special-wrapper')
        let today = new Date()

        const scroll_center = () => {
            this.state = 'none'
            let i = 0
            for (let schedule of this.specialMenus) {
                if (schedule.month === today.getMonth() + 1 && schedule.day === today.getDate()) {
                    this.currentIndex = i
                    special_wrapper.scrollLeft = 0.8 * (i + 1) * window.innerWidth
                    return
                }
                i++
            }
            this.currentIndex = Math.floor(this.specialMenus.length / 2)
            special_wrapper.scrollLeft = 0.8 * this.currentIndex * window.innerWidth
        }

        let touch_start_x = 0
        let touch_start_y = 0
        let is_flicked = false
        let flick_direction = 'left'
        special_wrapper.ontouchstart = (e) => {
            is_flicked = false
            touch_start_x = e.changedTouches[0].screenX;
            touch_start_y = e.changedTouches[0].screenY;
            special_wrapper.style.overflowX = 'hidden'
        }
        special_wrapper.ontouchend = (e) => {
            if (Math.abs(e.changedTouches[0].screenX - touch_start_x) > Math.abs(e.changedTouches[0].screenY - touch_start_y)) {
                is_flicked = true
                flick_direction = e.changedTouches[0].screenX > touch_start_x ? 'right' : 'left'
            }
            if (is_flicked) {
                if (flick_direction === 'left') {
                    scrollToRight()
                } else {
                    scrollToLeft()
                }
            }
        }

        const scrollToLeft = () => {
            if (this.currentIndex === 2) {
                let date = dateToStruct(previousWeekDay(this.specialMenus[0].month, this.specialMenus[0].day))
                getSpecialMenu([date]).then((data) => {
                    if (data.data.schedules.length !== 0) {
                        this.specialMenus = data.data.schedules.concat(this.specialMenus)
                        special_wrapper.scrollBy({top: 0, left: 0.8 * window.innerWidth, behavior: 'auto'})
                        this.state = 'right'
                    } else {
                        this.currentIndex--
                        scrollTo(this.currentIndex, 'left')
                    }
                }).catch(e => console.log(e))
            } else if (this.currentIndex !== -1) {
                this.currentIndex--
                scrollTo(this.currentIndex, 'left')
            }

        }

        function nextWeekDay(month, date) {
            let day = new Date((new Date()).getFullYear(), month - 1, date)
            day.setDate(day.getDate() + 1)
            if (day.getDay() === 0 || day.getDay() === 6) {
                day.setDate(day.getDate() + day.getDay() % 5 + 1)
            }
            return day
        }

        function previousWeekDay(month, date) {
            let day = new Date((new Date()).getFullYear(), month - 1, date)
            day.setDate(day.getDate() - 1)
            if (day.getDay() === 0 || day.getDay() === 6) {
                day.setDate(day.getDate() - (day.getDay() + 2) % 7)
            }
            return day
        }

        const scrollToRight = () => {
            if (this.currentIndex === this.specialMenus.length - 3) {
                let date = dateToStruct(nextWeekDay(this.specialMenus[this.specialMenus.length - 1].month, this.specialMenus[this.specialMenus.length - 1].day))
                getSpecialMenu([date])
                    .then((data) => {
                        this.specialMenus = this.specialMenus.concat(data.data.schedules)
                        this.state = 'left'
                    }).catch(e => console.log(e))
            } else {
                scrollTo(this.currentIndex, 'right')
            }
            if (this.currentIndex !== this.specialMenus.length) {
                this.currentIndex++
            }
        }

        let from = null
        let to = null
        let rAF = null
        let start = null

        const scrollTo = (index, direction) => {
            console.log([index, direction])
            if (direction === 'right' && this.canMoveRight) {
                from = special_wrapper.scrollLeft
                to = (index + 1) * 0.8 * window.innerWidth

                rAF = requestAnimationFrame(scrollAnimation)
                this.canMoveRight = false
            } else if (direction === 'left' && this.canMoveLeft) {
                from = special_wrapper.scrollLeft
                to = (index + 1) * 0.8 * window.innerWidth

                rAF = requestAnimationFrame(scrollAnimation)
                this.canMoveLeft = false
            }
        }

        const scrollAnimation = (timestamp) => {
            if (!start) start = timestamp
            let progress = timestamp - start;
            if (progress > 300) {
                cancelAnimationFrame(rAF)
                this.canMoveLeft = true
                this.canMoveRight = true

                start = null
                return
            }
            special_wrapper.scrollLeft = easeOutQuart(from, to, progress, 300)
            rAF = requestAnimationFrame(scrollAnimation)
        }

        if (this.state === 'first') {
            scroll_center()
        } else if (this.state === 'right') {
            scrollTo(this.currentIndex, 'left')
        } else if (this.state === 'left') {
            scrollTo(this.currentIndex, 'right')
        }
        this.state = 'none'
    },
    data: function () {
        return {
            specialMenus: [],
            currentIndex: 2,
            state: 'first',
            canMoveRight: true,
            canMoveLeft: true,
            loadedRight: true,
            loadedLeft: true
        }
    },
    methods: {
        setSpecial(specials) {
            this.$emit('input', specials);
        },
        setSoldOut: function (menuId, isSoldOut, name) {
            setSoldOut(menuId, isSoldOut, name)
        },
        likeThis: function (menu, toLike) {
            likeThis(menu, toLike)
        }
    }
})

Vue.component('permanent-menus', {
    template: `
           <div class="ui unstackable divided items permanent-wrapper">
           
            <div class="content">
               <h2 class="ui header special-container-header">
                  <img src="/static/images/udon.svg" class="ui image special-container-header-image">
                  <p>恒常メニュー</p>
               </h2>
            </div>
            
                <template v-for="menu in permanents">
      
              <div v-bind:class="{item: true, disabled: menu.is_sold_out }">
                
                <div class="image" v-bind:class="{blurred: menu.is_sold_out }">
                    <img v-bind:src='"/static/images/meal/"+menu.id+".jpg"' class="menu-image">
                </div>
                <div class="content">
                
                      <span class="header">
                      <i class="teal check icon hit-area" v-if="!menu.is_sold_out" v-on:click="setSoldOut(menu.id, true, menu.name)"></i>
                      <i class="red close icon hit-area" v-if="menu.is_sold_out" v-on:click="setSoldOut(menu.id, false, menu.name)"></i>
                      <span class="header-text">{{ menu.name }}</span>
                      </span>
                  <div class="meta flex-row" v-bind:class="{blurred: menu.is_sold_out }">
                    <span class="price">¥{{ menu.price }}</span>
                    <div class="ui right aligned">
                    <div class="ui left labeled button">
                      <a class="ui basic right pointing label">
                        {{ menu.like_count }}
                      </a>
                      <div class="ui red button" v-if="menu.is_liked" v-on:click="likeThis(menu, false)">
                        <i class="heart icon"></i> スキ
                      </div>
                      <div class="ui button" v-else v-on:click="likeThis(menu, true)">
                        <i class="heart icon"></i> スキ
                      </div>
                    </div>
                    </div>
                  </div>
                  <div class="extra" v-bind:class="{blurred: menu.is_sold_out }">
                    <div class="nutrition-wrapper-vertical">
                        <div class="nutrition-wrapper-horizontal">
                            <div class="nutrition">エネルギー: {{ menu.nutrition.energy }} kcal</div>
                            <div class="nutrition">脂質: {{ menu.nutrition.fat }} kcal</div>
                        </div>
                        <div class="nutrition-wrapper-horizontal">
                            <div class="nutrition">タンパク質: {{ menu.nutrition.protein }} g</div>
                            <div class="nutrition">塩分: {{ menu.nutrition.salt }} g</div>
                        </div>
                    </div>
                  </div>
                </div>
              </div>
              </template>
            </div>`,
    mounted: async function () {
        let result = await getPermanentMenu()
        this.permanents = result.data.menus
        this.permanents.sort((a, b) => {
            if (a.name > b.name) return 1
            if (a.name < b.name) return -1
            return 0
        })
        this.setPermanent(this.permanents)
    },
    data: function () {
        return {
            permanents: [],
        }
    },
    methods: {
        setPermanent(permanent) {
            this.$emit('input', permanent);
        },
        setSoldOut: function (menuId, isSoldOut, name) {
            setSoldOut(menuId, isSoldOut, name)
        },
        likeThis: function (menu, toLike) {
            likeThis(menu, toLike)
        }
    }
})

const app = new Vue({
    el: '#app',
    data: {
        specialMenus: [],
        permanent: [],
        isLoggedIn: false,
        mailAddress: null,
        name: null,
        sub: null,
        socket: null,
        congestion: null,
        needWalkThrough: false,
        walkThroughIndex: 0,
        walkThroughIndexMax: 6,
        getNext: null
    },
    mounted: function () {
        const isTourEnded = () => {
            let data = getCookie('tour')
            return (data !== null)
        }

        this.setTourEnded = () => {
            this.needWalkThrough = !isTourEnded()
            if (this.needWalkThrough) {
                let elem = document.getElementById('walk-through-container')
                if (elem !== null) {
                    elem.style.display = 'block'
                    $(elem).on('touchmove.noScroll', function (e) {
                        e.preventDefault();
                    });
                }
            }
        }

        gapi.load('auth2', () => {
            initGoogleAuth()
            if (isGoogleSignedIn()) {
                this.mailAddress = getEmail()
                this.name = getName()
                this.isLoggedIn = true
            }
            let elem = document.getElementById('accountWrapper')
            if (elem) {
                elem.classList.remove('hidden')
            }

            loadLikes()
            loadCongestion()
        })

        const url = new URL(window.location);
        if (location.protocol.startsWith('https')) {
            this.socket = new WebSocket(`wss://${url.hostname}:${url.port}/api/v1/ws`);
        } else {
            this.socket = new WebSocket(`ws://${url.hostname}:${url.port}/api/v1/ws`);
        }

        this.socket.onopen = function (e) {
            console.log("[open] Connection established");
        };

        this.socket.onmessage = (event) => {
            console.log(`[message] Data received from server: ${event.data}`);

            let data = JSON.parse(event.data)
            if (data.method === 'sold_out') {
                setSoldOut(data)
            } else if (data.method === 'congestion') {
                setCongestion(data)
            }
        };

        const setSoldOut = (data) => {
            for (let schedule of this.specialMenus) {
                if (schedule.a_menu.id === data.id) {
                    schedule.a_menu.is_sold_out = data.is_sold_out
                    return
                } else if (schedule.b_menu.id === data.id) {
                    schedule.b_menu.is_sold_out = data.is_sold_out
                    return
                }
            }
            for (let menu of this.permanent) {
                if (menu.id === data.id) {
                    menu.is_sold_out = data.is_sold_out
                    return
                }
            }
        }

        this.socket.onclose = function (event) {
            if (event.wasClean) {
                console.log(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
            } else {
                console.log('[close] Connection died');
            }
        };

        this.socket.onerror = function (error) {
            console.log(`[error] ${error.message}`);
        };


    },
    methods: {

        postCongestion(congestion) {
            const func = () => {
                if (confirm(`混雑度を ${'小中大'[congestion]} に変更します。\nよろしいですか？`)) {
                    axios.post('/api/v1/congestion', {
                        congestion: congestion,
                        token: getIdToken()
                    }).then((response) => {

                    }).catch((e) => {
                        if (e.response.status === 429) {
                            alert('リクエストが頻繁過ぎます')
                        } else {
                            alert('失敗しました')
                        }
                    });
                }
            }
            if (!isGoogleSignedIn()) {

                if (!signIn(func)) {
                    alert('Googleログインに失敗しました')
                }
            } else {
                func()
            }
        },
        nextWalkThrough() {
            this.getNext = new Date()
            this.walkThroughIndex++
            if (this.walkThroughIndex >= this.walkThroughIndexMax) {
                this.needWalkThrough = false
                document.cookie = 'tour=end'
            }
        },
        previousWalkThrough() {
            this.walkThroughIndex--
        }
    },
    updated: function () {
        this.setTourEnded()
    }
})

const setSoldOut = (menuId, isSoldOut, name) => {
    const func = () => {
        if (confirm(`${name}を ${isSoldOut ? '売り切れ' : '販売中'} に変更します。\nよろしいですか？`)) {
            axios.post('/api/v1/sold-out', {
                menu_id: menuId,
                is_sold_out: isSoldOut,
                token: getIdToken()
            }).then((response) => {

            }).catch((e) => {
                if (e.response.status === 429) {
                    alert('リクエストが頻繁過ぎます')
                } else {
                    alert('失敗しました')
                }
            });
        }
    }
    if (!isGoogleSignedIn()) {
        if (!signIn(func)) {
            alert('Googleログインに失敗しました')
        }
    } else {
        func()
    }
}


function likeThis(menu, toLike) {
    const func = () => {
        if (toLike) {
            menu.is_liked = true
            menu.like_count++
            axios.post('/api/v1/like', {
                token: getIdToken(),
                menu_id: menu.id
            }).then(res => {

            }).catch(() => {
                menu.is_liked = false
                menu.like_count--
                setTimeout(() => alert('スキに失敗しました'), 100)
            })
        } else {
            menu.is_liked = false
            menu.like_count--
            axios.delete('/api/v1/like', {
                params: {
                    token: getIdToken(),
                    menu_id: menu.id
                }
            }).then(res => {

            }).catch(() => {
                menu.is_liked = true
                menu.like_count++
                setTimeout(() => alert('スキの消去に失敗しました'), 100)
            })
        }
    }
    if (!isGoogleSignedIn()) {
        if (!signIn(func)) {
            alert('Googleログインに失敗しました')
        }
    } else {

        func()
    }
}


const loadLikes = () => {
    console.log('loadLike')
    if (!isGoogleSignedIn()) {
        console.log('not!')
        return
    }

    let token = getIdToken()
    return axios.get('/api/v1/like/me', {
        params: {
            token: token
        }
    }).then(res => {
        let data = res.data
        for (let schedule of app.specialMenus) {
            schedule.a_menu.is_liked = data.likes.includes(schedule.a_menu.id)
            schedule.b_menu.is_liked = data.likes.includes(schedule.b_menu.id)
        }
        for (let menu of app.permanent) {
            menu.is_liked = data.likes.includes(menu.id)
        }
    })
}

const loadCongestion = () => {
    console.log('loadCongestion')

    return axios.get('/api/v1/congestion'
    ).then(res => {
        let data = res.data
        app.congestion = data.congestion

        setTimeout(() => {
            $('#congestion-icon-wrapper')
                .popup({
                    popup: '#congestion-selector',
                    position: 'bottom center',
                    on: 'click',
                    hideOnScroll: true,
                    onShow: function () {
                        $(window)
                            .one('scroll', function () {
                                $('#congestion-icon-wrapper').popup('#congestion-selector');
                            })
                        ;
                    }
                });
        }, 100)

    })
}

const setCongestion = (data) => {
    app.congestion = data.congestion
}


const signOut = () => {
    gapi.auth2.getAuthInstance().disconnect()

    document.cookie = `token=; max-age=0`
    document.cookie = `email=; max-age=0`
    document.cookie = `name=; max-age=0`

    app.mailAddress = null
    app.isLoggedIn = false
    app.name = null

    for (let schedule of app.specialMenus) {
        schedule.a_menu.is_liked = false
        schedule.b_menu.is_liked = false

    }
    for (let menu of app.permanent) {
        menu.is_liked = false
    }
}

const signIn = (callback) => {
    gapi.auth2.getAuthInstance().signIn().then((data) => {
        document.cookie = `token=${getIdToken()}`
        document.cookie = `email=${getEmail()}`
        document.cookie = `name=${encodeURIComponent(getName())}`

        app.mailAddress = getEmail()
        app.name = getName()
        app.isLoggedIn = true

        callback()
        return true
    }).catch(err => {
        return false
    });
}