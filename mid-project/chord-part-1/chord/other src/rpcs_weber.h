#ifndef RPCS_H
#define RPCS_H

#include "chord.h"
#include "rpc/client.h"

#include <cmath>
#include <iostream>
#include <cstdint>

Node self, successor, predecessor;
bool hasError = false;

Node get_info() { return self; } // Do not modify this line.
Node get_predecessor() { return predecessor; }
Node get_successor() { return successor; }

/** 
 * takes three arguments (x, a, and b) 
 * returns true if x is between a and b (exclusive) and false otherwise (不包含頭尾)
 */
bool isBetween(uint64_t x, uint64_t a, uint64_t b) {
  if (b > a){
    return x > a && x < b;
  }
  // case: 3x is in (8a, 5b)
  return x > a || x < b;
}

bool isBetween_inclusive(uint64_t x, uint64_t a, uint64_t b){
  if (b > a) {
    if (x > a && x <= b) {
      return true;
    } else {
      return false;
    }
  } else { // successor_id <= predecessor_id
    if ( x > a || x <= b) {
      return true;
    } else {
      return false;
    }
  }
}

bool isBetween(uint64_t id, uint64_t predecessor_id, uint64_t successor_id){
  if (successor_id > predecessor_id) {
    if (id > predecessor_id && id < successor_id) {
      return true;
    } else {
      return false;
    }
  } else { // successor_id <= predecessor_id
    if ( id > predecessor_id || id < successor_id) {
      return true;
    } else {
      return false;
    }
  }
}

void create() {
  predecessor.ip = "";
  successor = self;
}


/**
 * New Node n join chord ring. Assign a successor to him.
*/
void join(Node n) {
  predecessor.ip = "";
  rpc::client client(n.ip, n.port);
  successor = client.call("find_successor", self.id).as<Node>();
  std::cout << self.id << " join(), successor is "<< successor.id << std::endl;
}

/**
 * Ask node n to find the successor of id
*/
// Node find_successor(uint64_t id) {
//   // successor (繼任) 我下一個Node是誰
//   // TODO: implement your `find_successor` RPC
//   std::cout << self.id << " find_successor(), to find "<< id << std::endl;
//   if (successor.id == self.id){ // 網路中只有自己時，return 自己
//     std::cout << self.id << " i'm successor of "<< id << std::endl;
//     return self;
//   }
//   if (isBetween(id, self.id, successor.id) || id == successor.id) { // 繼任者剛好負責這個 id, return
//     std::cout << self.id << " i'm successor of "<< id << std::endl;
//     return successor;
//   }
//   else { // 繼任者不是，遞迴呼叫
//     rpc::client s(successor.ip, successor.port); 
//     return s.call("find_successor", id).as<Node>();
//   }
// }
Node find_successor(uint64_t id) {
  // TODO: implement your `find_successor` RPC
  try {

    // if ( self.id == successor.id ){ // only one node

    //   return successor;
    if ( isBetween_inclusive(id, self.id, successor.id) ){
      return successor;
    } else {
      // Node closest_node = closest_preceding_node(id);
      // rpc::client client(closest_node.ip, closest_node.port); 
      // return client.call("find_successor", id).as<Node>();

      rpc::client client(successor.ip, successor.port); 
      return client.call("find_successor", id).as<Node>();
    }

  } catch (std::exception &e) {
    successor.ip = "";
    std::cout << "find_successor err" << "\n" ;
  }
  return self;
}

void check_predecessor() {
  // predecessor (前任) 我上一個Node是誰
  // 如果指向我的Node失聯，清空ip，標示他已下線
  try {
    rpc::client client(predecessor.ip, predecessor.port);
    Node n = client.call("get_info").as<Node>();
  } catch (std::exception &e) {
    predecessor.ip = "";
  }
}

/**
 * stabilize() 檢查我和繼任者中間是否被插隊，有則換掉我的繼任者為n'，並通知繼任者n'。
*/
// void stablize(){

//   try {

//     Node pre_node;
//     // uint64_t temp_su_id = successor.id;
//     // std::cout << "Node:" << self.id << "\n";
//     // std::cout << "    temp id:" << temp_su_id << "\n";

//     // std::cout << "IN sta:" << self.port << ":" << successor.port << "\n";
//     if ( successor.id != 0 && self.id != successor.id ) {

//       rpc::client client(successor.ip, successor.port); 
//       pre_node = client.call("get_predecessor").as<Node>();

//     } else { // when only have root node [self.id == successor.id]
//       pre_node = predecessor;
//       // std::cout << "IN sta:" << pre_node.id << "\n";
//     }

//     if (pre_node.id != 0) { // check if pre_node exist. if exist, check weather to change the successor

//       if ( inOpenRange(pre_node.id, self.id, successor.id) ) {
//         successor = pre_node;
//         // std::cout << "    change id:" << successor.id << "\n";
//       } 
//     } 
    
//     if ( successor.id != 0 && self.id != successor.id) {
//       // if (temp_su_id != successor.id) { // if successor change, tell it to change predecessor
//       rpc::client client2(successor.ip, successor.port);
//       // std::cout << "Notify Node  :" << successor.port << "\n";
//       client2.call("notify", self);   
//       // }
//     }

//   } catch (std::exception &e) {
//     // std::cout << &e. << "\n" ;
//     std::cout << "stablize Err \n";

//   }

// }
void stablize(){
  try {
    rpc::client *s;
    Node candidate_s;

    if ( successor.id != 0 && self.id != successor.id ) {
      // get successor.predecessor (沒被插隊的話，會是我自己)
      // std::cout << "stablize: " << self.id << " call get_predecessor on " << successor.id << std::endl;
      s = new rpc::client(successor.ip, successor.port);
      candidate_s = s->call("get_predecessor").as<Node>();
    } else { 
      // when only have root node [self.id == successor.id]
      candidate_s = predecessor;
    }
    // no nessesary to print
    // std::cout << "stablize: " << self.id << "'s candidate_s is " << candidate_s.id << " current succ is " << successor.id << std::endl;

    // check 是否被別人插隊，如果有則插隊的人是我的新 successor
    // if (s <- p <- n), p is my new successor
    if (candidate_s.id != 0) { 
      if ( isBetween(candidate_s.id, self.id, successor.id) ) {
        successor = candidate_s;
      } 
    } 
    
    // notify successor that i'm yours predecessor
    if ( successor.id != 0 && self.id != successor.id) {
      s = new rpc::client(successor.ip, successor.port);
      s->call("notify", self);  
    }
  } catch (std::exception &e) {
    if (!hasError){
      std::cout << "chord stablize error at " << self.id << "\n";
      hasError = true;
    }
  }
}

/**
 * Only called by predecessor. Node `notifier` thinks he is might be my predecessor.
 * If notifier's id is smaller then my current predecessor, change to `notifier`.
*/
void notify(Node notifier) {
  rpc::client s(successor.ip, successor.port);
  if ( predecessor.ip == "" || isBetween(notifier.id, predecessor.id, self.id) ) {
    predecessor = notifier;
    std::cout <<"notify: "<< self.id << ": was notify(), change predecessor to"<< notifier.id << std::endl;
  }
}

void register_rpcs() {
  add_rpc("get_info", &get_info); // Do not modify this line.
  add_rpc("create", &create);
  add_rpc("join", &join);
  add_rpc("get_predecessor", &get_predecessor);
  add_rpc("get_successor", &get_successor);
  add_rpc("find_successor", &find_successor);
  add_rpc("notify", &notify);
}

void register_periodics() {
  add_periodic(check_predecessor);
  add_periodic(stablize);
}

#endif /* RPCS_H */
