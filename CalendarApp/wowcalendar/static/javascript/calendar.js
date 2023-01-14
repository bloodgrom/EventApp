selected_day_global = "01"
selected_month_global = "01"
selected_year_global = "01"



!function() {

  var today = moment();
  date_headline = createElement('h4', 'day-date-header', '')

  function Calendar(selector, events) {
    this.el = document.querySelector(selector);
    this.events = events;
    this.current = moment().date(1);
    this.draw();
    
    var current = document.querySelector('.today');
    if(current) {
      var self = this;
      window.setTimeout(function() {
        self.openDay(current);
      }, 500);
    }
  }

  Calendar.prototype.draw = function() {
    //Create Header
    this.drawHeader();

    //Draw Month
    this.drawMonth();

    var myInterval = setInterval(getSetCurrentDayInput, 1000);

    //this.drawLegend();
  }

  Calendar.prototype.drawHeader = function() {
    var self = this;
    if(!this.header) {
      //Create the header elements
      this.header = createElement('div', 'header');
      this.header.className = 'header';

      this.title = createElement('h1');

      var right = createElement('div', 'right');
      right.addEventListener('click', function() { self.nextMonth(); });

      var left = createElement('div', 'left');
      left.addEventListener('click', function() { self.prevMonth(); });

      //Append the Elements
      this.header.appendChild(this.title); 
      this.header.appendChild(right);
      this.header.appendChild(left);
      this.el.appendChild(this.header);
    }

    this.title.innerHTML = this.current.format('MMMM YYYY');
  }

  Calendar.prototype.drawMonth = function() {
    var self = this;
    
    this.events.forEach(function(ev) {

      var dateString = ev.start_date[0] + "-" + ev.start_date[1] + "-" + ev.start_date[2]
      const momentDate = moment(dateString, 'DD-MM-YYYY')
      ev.date = momentDate
      ev.color = "yellow"
      
    });
    
    
    if(this.month) {
      this.oldMonth = this.month;
      this.oldMonth.className = 'month out ' + (self.next ? 'next' : 'prev');
      this.oldMonth.addEventListener('webkitAnimationEnd', function() {
        self.oldMonth.parentNode.removeChild(self.oldMonth);
        self.month = createElement('div', 'month');
        self.backFill();
        self.currentMonth();
        self.fowardFill();
        self.el.appendChild(self.month);
        window.setTimeout(function() {
          self.month.className = 'month in ' + (self.next ? 'next' : 'prev');
        }, 16);
      });
      
    } else {
        this.month = createElement('div', 'month');
        this.el.appendChild(this.month);
        this.backFill();
        this.currentMonth();
        this.fowardFill();
        this.month.className = 'month new';
    }


  }

  Calendar.prototype.backFill = function() {
    var clone = this.current.clone();
    var dayOfWeek = clone.day();

    if(!dayOfWeek) { return; }

    clone.subtract('days', dayOfWeek+1);

    for(var i = dayOfWeek; i > 0 ; i--) {
      this.drawDay(clone.add('days', 1));
    }
  }

  Calendar.prototype.fowardFill = function() {
    var clone = this.current.clone().add('months', 1).subtract('days', 1);
    var dayOfWeek = clone.day();

    if(dayOfWeek === 6) { return; }

    for(var i = dayOfWeek; i < 6 ; i++) {
      this.drawDay(clone.add('days', 1));
    }
  }

  Calendar.prototype.currentMonth = function() {
    var clone = this.current.clone();

    while(clone.month() === this.current.month()) {
      this.drawDay(clone);
      clone.add('days', 1);
    }
  }

  Calendar.prototype.getWeek = function(day) {
    if(!this.week || day.day() === 0) {
      this.week = createElement('div', 'week');
      this.month.appendChild(this.week);
    }
  }

  Calendar.prototype.drawDay = function(day) {
    var self = this;
    this.getWeek(day);

    //Outer Day
    var outer = createElement('div', this.getDayClass(day));
    outer.addEventListener('click', function() {
      self.openDay(this);
    });

    //Day Name
    var name = createElement('div', 'day-name', day.format('ddd'));

    //Day Number
    var number = createElement('div', 'day-number', day.format('DD'));


    //Events
    var events = createElement('div', 'day-events');
    this.drawEvents(day, events);

    outer.appendChild(name);
    outer.appendChild(number);
    outer.appendChild(events);
    
    this.week.appendChild(outer);
  }
  
  Calendar.prototype.drawEvents = function(day, element) {
    if(day.month() === this.current.month()) {
      var todaysEvents = this.events.reduce(function(memo, ev) {
        
        if(ev.date.isSame(day, 'day')) {
          memo.push(ev);
        }
        return memo;
      }, []);

      todaysEvents.forEach(function(ev) {
        var evSpan = createElement('span', ev.color);
        element.appendChild(evSpan);
      });
    }
  }

  Calendar.prototype.getDayClass = function(day) {
    classes = ['day'];
    if(day.month() !== this.current.month()) {
      classes.push('other');
    } else if (today.isSame(day, 'day')) {
      classes.push('today');
    }
    return classes.join(' ');
  }


  Calendar.prototype.openDay = function(el) {
    var details;
    var dayNumber = +el.querySelectorAll('.day-number')[0].innerText || +el.querySelectorAll('.day-number')[0].textContent;
    var day = this.current.clone().date(dayNumber);

    var currentOpened = document.querySelector('.details');

    //Check to see if there is an open detais box on the current row
    if(currentOpened && currentOpened.parentNode === el.parentNode) {
      details = currentOpened;
    } else {
      //Close the open events on differnt week row
      //currentOpened && currentOpened.parentNode.removeChild(currentOpened);
      if(currentOpened) {
        currentOpened.addEventListener('webkitAnimationEnd', function() {
          currentOpened.parentNode.removeChild(currentOpened);
        });
        currentOpened.addEventListener('oanimationend', function() {
          currentOpened.parentNode.removeChild(currentOpened);
        });
        currentOpened.addEventListener('msAnimationEnd', function() {
          currentOpened.parentNode.removeChild(currentOpened);
        });
        currentOpened.addEventListener('animationend', function() {
          currentOpened.parentNode.removeChild(currentOpened);
        });
        currentOpened.className = 'details out';
      }

      //Create the Details Container
      details = createElement('div', 'details in');

      //Create the arrow
      //var arrow = createElement('div', 'arrow');

      //Create the event wrapper

      //details.appendChild(arrow);
      el.parentNode.appendChild(details);

      var self = this;
      this.getWeek(day);
      
      selected_day_global = day.format('DD')
      selected_month_global = this.current.format('MM');
      selected_year_global = this.current.format('YYYY');
      
      // var calendarDay = selected_day_global
      var calendarMonth = this.current.format('MM');
      var calendarYear = this.current.format('YYYY');

      var full_date = calendarYear.toString() + "-" + calendarMonth.toString() + "-" + selected_day_global.toString()
      var django_param = "?date=" + full_date

      if (has_permission == 1) {
        var add_event_link = createElement('a', 'event-button', "+");
        add_event_link.setAttribute('href', url_django+django_param);

        details.appendChild(add_event_link);
      }
    }

    var todaysEvents = this.events.reduce(function(memo, ev) {
      if(ev.date.isSame(day, 'day')) {
        memo.push(ev);
      }
      return memo;
    }, []);

    this.renderEvents(todaysEvents, details);

    //arrow.style.left = el.offsetLeft - el.parentNode.offsetLeft + 27 + 'px';
  }

  Calendar.prototype.renderEvents = function(events, ele) {
    //Remove any events in the current details element
    var currentWrapper = ele.querySelector('.events');
    var wrapper = createElement('div', 'events in' + (currentWrapper ? ' new' : ''));

    var current_date = selected_day_global + "." + selected_month_global + "." + selected_year_global
    date_headline.innerHTML = current_date
    var separate_line = createElement('hr', '', '')

    wrapper.appendChild(date_headline);
    wrapper.appendChild(separate_line);

    events.forEach(function(ev) {

      console.log(ev.date)
      console.log(ev.start_date[0])

      var event_day_start = ev.start_date[0]
      var event_month_start = ev.start_date[1]
      var event_year_start = ev.start_date[2]

      // var full_date = event_day_start.toString() + "." + event_month_start.toString() + "." + event_year_start
      // var django_param = "?date=" + full_date
      var event_id = ev.event_id
      var django_param = "?event_id=" + event_id

      if (event_day_start < 10) {
        event_day_start = "0" + event_day_start.toString()
      }

      if (event_month_start < 10) {
        event_month_start = "0" + event_month_start.toString()
      }

      var event_day_end = ev.end_date[0]
      var event_month_end = ev.end_date[1]
      var event_year_end = ev.end_date[2]

      if (event_day_end < 10) {
        event_day_end = "0" + event_day_end.toString()
      }

      if (event_month_end < 10) {
        event_month_end = "0" + event_month_end.toString()
      }

      var start_time = ev.start_time
      var end_time = ev.end_time
      var deadline = ev.deadline

      var div = createElement('div', 'event generic-link-dark');
      var square = createElement('div', 'event-category ' + ev.color);
      //<a href="{% url 'logout' %}">Logout</a>
      //&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
      //&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
      //&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
      var event_link = createElement('a', '', ev.eventName);
      event_link.setAttribute('href', url_django_view+django_param);
      //-----------------------------------
      var dashbreak = createElement('span', '', " - ");
      var span2 = createElement('span', '', ev.description);
      var breakline = createElement('br', '', "");
      var event_time = createElement('span', '', event_day_start +
                                                 "." + 
                                                 event_month_start + 
                                                 " from " + 
                                                 start_time +
                                                 " to " +
                                                 event_day_end +
                                                 "." +
                                                 event_month_end +
                                                 " at " +
                                                 end_time
                                                 );
      var breakline2 = createElement('br', '', "");
      var event_dealine = createElement('span', '', "Deadline: " + deadline);
      //-----------------------------------

      div.appendChild(square);
      div.appendChild(event_link);
      //-----------------------------------
      div.appendChild(dashbreak);
      div.appendChild(span2);
      div.appendChild(breakline);
      div.appendChild(event_time);
      div.appendChild(breakline2);
      div.appendChild(event_dealine);
      //-----------------------------------
      wrapper.appendChild(div);
    });

    if(!events.length) {
      var div = createElement('div', 'event empty');
      var span = createElement('span', '', 'No Events');

      div.appendChild(span);
      wrapper.appendChild(div);
    }

    if(currentWrapper) {
      currentWrapper.className = 'events out';
      currentWrapper.addEventListener('webkitAnimationEnd', function() {
        currentWrapper.parentNode.removeChild(currentWrapper);
        ele.appendChild(wrapper);
      });
      currentWrapper.addEventListener('oanimationend', function() {
        currentWrapper.parentNode.removeChild(currentWrapper);
        ele.appendChild(wrapper);
      });
      currentWrapper.addEventListener('msAnimationEnd', function() {
        currentWrapper.parentNode.removeChild(currentWrapper);
        ele.appendChild(wrapper);
      });
      currentWrapper.addEventListener('animationend', function() {
        currentWrapper.parentNode.removeChild(currentWrapper);
        ele.appendChild(wrapper);
      });
    } else {
      ele.appendChild(wrapper);
    }
  }

  // Calendar.prototype.drawLegend = function() {
  //   var legend = createElement('div', 'legend');
  //   var calendars = this.events.map(function(e) {
  //     return e.calendar + '|' + e.color;
  //   }).reduce(function(memo, e) {
  //     if(memo.indexOf(e) === -1) {
  //       memo.push(e);
  //     }
  //     return memo;
  //   }, []).forEach(function(e) {
  //     var parts = e.split('|');
  //     var entry = createElement('span', 'entry ' +  parts[1], parts[0]);
  //     legend.appendChild(entry);
  //   });
  //   this.el.appendChild(legend);
  // }

  Calendar.prototype.nextMonth = function() {
    this.current.add('months', 1);
    this.next = true;
    this.draw();
  }

  Calendar.prototype.prevMonth = function() {
    this.current.subtract('months', 1);
    this.next = false;
    this.draw();
  }

  window.Calendar = Calendar;

  function createElement(tagName, className, innerText) {
    var ele = document.createElement(tagName);
    if(className) {
      ele.className = className;
    }
    if(innerText) {
      ele.innderText = ele.textContent = innerText;
    }
    return ele;
  }
}();

!function() {

  //start_date = [day, month, year]
  var events_example = [
    {
      eventName : 'Vault of Incarnates',
      start_date : [7,1,2023],
      end_date : [7,1,2023],
      start_time : "21:00",
      end_time: "24:00",
      deadline: "16:30",
      description: "Пред инстанцията в 20:45"
    },

    {
      eventName : 'Vault of Incarnates',
      start_date : [19,1,2023],
      end_date : [20,1,2023],
      start_time : "23:00",
      end_time: "02:00",
      deadline: "18:30",
      description: "Пред инстанцията в 22:45"
    },
  ];


  var events_json_fixed = events_json.replace(/&quot;/g,'\"');
  var events_array =  JSON.parse(events_json_fixed);

  console.log(events_array)


  // function addDate(ev) {
    
  // }

  var calendar = new Calendar('#calendar', events_array);
}();

function getSetCurrentDayInput() {

  var all_days = document.getElementsByClassName('day');
  for (var i = 0; i < all_days.length; ++i) {

    (function () {
      var day_div = all_days[i];
      var classList = Array.from(day_div.classList);

      if (classList.length == 1) {
        var day_num_div = day_div.querySelector(".day-number");
        var day_text = day_num_div.innerHTML

        if (!day_div.hasAttribute('listenerOnClick')) {
          day_div.addEventListener("click", function setDayText(){
            document.getElementById("selected_day").value = day_text;
            selected_day_global = day_text;
            console.log(selected_day_global)

            var all_day_links = document.getElementsByClassName('event-button');
            for (var i = 0; i < all_day_links.length; ++i) {

              var full_date = selected_year_global.toString() + "-" + selected_month_global.toString() + "-" + selected_day_global.toString()
              var django_param = "?date=" + full_date

              var current_date = selected_day_global + "." + selected_month_global + "." + selected_year_global
              date_headline.innerHTML = current_date

              var a_link = all_day_links[i];
              a_link.href = url_django + django_param
            }
          });
          day_div.setAttribute('listenerOnClick', 'true');
        }
      }
    }());
  }
}

