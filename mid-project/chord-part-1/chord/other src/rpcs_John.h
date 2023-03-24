#ifndef RPCS_H
#define RPCS_H

#include "chord.h"
#include "rpc/client.h"

#include <cmath>
#include <iostream>
#include <cstdint>

Node self, successor, predecessor;
Node finger_table[4];

Node get_info() { return self; } // Do not modify this line.
Node get_predecessor() { return predecessor; }
Node get_successor() { return successor; }
Node get_finger_table_0() {return finger_table[0]; }
Node get_finger_table_3() {return finger_table[3]; }


void create() {
  predecessor.ip = "";
  successor = self;
}

void change_predecessor(Node n) {
  predecessor = n;
}

void change_successor(Node n) {
  successor = n;
}

void join(Node n) { // n is a known node on Chrod ring
  predecessor.ip = "";
  rpc::client client(n.ip, n.port); // get the known node instance

  successor = client.call("find_successor", self.id).as<Node>(); // use the known node to find the successor by new node id
}

bool inCloseRange(uint64_t id, uint64_t predecessor_id, uint64_t successor_id){
  if (successor_id > predecessor_id) {
    if (id > predecessor_id && id <= successor_id) {
      return true;
    } else {
      return false;
    }
  } else { // successor_id <= predecessor_id
    if ( id > predecessor_id || id <= successor_id) {
      return true;
    } else {
      return false;
    }
  }
}

bool inOpenRange(uint64_t id, uint64_t predecessor_id, uint64_t successor_id){
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

Node closest_preceding_node (uint64_t id) {
  for ( int i = 3; i > 0; i-- ) {
    
    if ( inOpenRange(finger_table[i].id, self.id, id) ) {
      return finger_table[i];
    }

    // if ( finger_table[i].id > self.id && finger_table[i].id < id) {
    //   return finger_table[i];
    // }
  }

  return self;
}

/* finger table version */
Node find_successor(uint64_t id) {
  // TODO: implement your `find_successor` RPC
  try {

    // if ( self.id == successor.id ){ // only one node

    //   return successor;
    if ( inCloseRange(id, self.id, successor.id) ){
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

// /* finger table version */
// Node find_successor(uint64_t id) {
//   // TODO: implement your `find_successor` RPC
//   try {

//     // if ( self.id == successor.id ){ // only one node

//     //   return successor;

//     if ( id > self.id ){ 

//       if (successor.id > self.id) { // not out the max range

//         // In range [self, successor]
//         if (id < successor.id) { 
//           return successor;

//         // out range [self, successor]
//         } else { 
//           Node closest_node = closest_preceding_node(id);
//           rpc::client client(closest_node.ip, closest_node.port); // get the known node instance
//           return client.call("find_successor", id).as<Node>();
//         }
//       } else { // if successor.id out of max range, it may <= self.id
        
//         return successor;
//       }
 
//     } else { // id <= self.id
//       Node closest_node = closest_preceding_node(id);
//       rpc::client client(closest_node.ip, closest_node.port); // get the known node instance
//       return client.call("find_successor", id).as<Node>();
//     }

//     // // how to get the successor.id?
//     // if (id > self.id && id < successor.id ) {

//     // }

//   } catch (std::exception &e) {
//     successor.ip = "";
//     std::cout << "find_successor err" << "\n" ;
//   }
//   return self;
// }

uint64_t MAX = UINT64_MAX;
uint64_t STEP = UINT64_MAX / 16;
uint64_t next = 0;
void fix_fingers(){
  try {
    if (next >= 4){
      next = 0;
    }
    finger_table[next] = find_successor(self.id + (next+1)*STEP );
    next = next + 1;
  } catch (std::exception &e) {
    std::cout << "fix_fingers err" << "\n" ;
  } 
}
/* No Finger table*/
// Node find_successor(uint64_t id) {
//   // TODO: implement your `find_successor` RPC
//   try {

//     if ( self.id == successor.id ){ // only one node

//       return successor;
//     } else if ( id > self.id && id < successor.id){ // id in the range of [self, successor]

//       return successor;
//     } else { // if not in the range [self, successor], ask next node to find successor

//       rpc::client client(successor.ip, successor.port); // get the known node instance
//       return client.call("find_successor", id).as<Node>();
//     }

//     // // how to get the successor.id?
//     // if (id > self.id && id < successor.id ) {

//     // }

//   } catch (std::exception &e) {
//     successor.ip = "";
//   }
//   return self;
// }

void stablize(){
  try {

    Node pre_node;
    // std::cout << "IN sta:" << self.port << ":" << successor.port << "\n";
    if ( successor.id != 0 && self.id != successor.id ) {
      rpc::client client(successor.ip, successor.port); 
      pre_node = client.call("get_predecessor").as<Node>();     
    } else {
      pre_node = predecessor;
      // std::cout << "IN sta:" << pre_node.id << "\n";
    }

    if (pre_node.id != 0) { // check if pre_node exist. if exist, check weather to change the successor

      if ( inOpenRange(pre_node.id, self.id, successor.id) ) {
        successor = pre_node;
      } 
    } 
    
    if ( successor.id != 0 && self.id != successor.id) {
      rpc::client client2(successor.ip, successor.port);
      // std::cout << "Notify Node  :" << successor.port << "\n";
      client2.call("notify", self);   
    }

  } catch (std::exception &e) {
    // std::cout << &e. << "\n" ;
    std::cout << "stablize Err \n";
  }

}


// void stablize(){
//   try {

//     Node pre_node;
//     // std::cout << "IN sta:" << self.port << ":" << successor.port << "\n";
//     if ( successor.id != 0 && self.id != successor.id ) {
//       rpc::client client(successor.ip, successor.port); 
//       pre_node = client.call("get_predecessor").as<Node>();     
//     } else {
//       pre_node = predecessor;
//       // std::cout << "IN sta:" << pre_node.id << "\n";
//     }

//     // rpc::client client(successor.ip, successor.port); 
//     // Node pre_node = client.call("get_predecessor").as<Node>();

//     if (pre_node.id != 0) { // check if pre_node exist. if exist, check weather to change the successor


//       if (successor.id > self.id && pre_node.id > self.id){
//         successor = pre_node;
//       } else if (successor.id  < self.id) { 
//         if (pre_node.id < successor.id){
//           successor = pre_node;
//         } else { // pre_node.id > successor.id
//           if (pre_node.id > self.id){
//             successor = pre_node;
//           }
//         }
//       } else if (successor.id == self.id) { // only root node will trigger
//         successor = pre_node;
//       }
//     } 
    
    
//     if ( successor.id != 0 && self.id != successor.id) {
//       rpc::client client2(successor.ip, successor.port);
//       // std::cout << "Notify Node  :" << successor.port << "\n";
//       client2.call("notify", self);   
//     }

//   } catch (std::exception &e) {
//     // std::cout << &e. << "\n" ;
//     std::cout << "stablize Err \n";
//   }

// }

void notify(Node n){
  // std::cout << "In notify  :" << self.port << "\n";
  // std::cout << "In notify  :" << predecessor.ip << "\n";

  if ( predecessor.ip == "" || inOpenRange(n.id, predecessor.id, self.id) ) {
    predecessor = n;
    // std::cout << "notify()" << "\n" ;
  }

  // if ( predecessor.ip == "" || (n.id > predecessor.id && n.id < self.id)  ) {
  //   predecessor = n;
  //   // std::cout << "notify()" << "\n" ;
  // }
}

void check_predecessor() {
  try {
    rpc::client client(predecessor.ip, predecessor.port);
    Node n = client.call("get_info").as<Node>();
  } catch (std::exception &e) {
    predecessor.ip = "";
    // std::cout << "check_predecessor Err \n";
  }
}

void register_rpcs() {
  add_rpc("get_info", &get_info); // Do not modify this line.

  add_rpc("get_predecessor", &get_predecessor); 
  add_rpc("change_predecessor", &change_predecessor);
  add_rpc("get_successor", &get_successor);
  add_rpc("change_successor", &change_successor);
  add_rpc("notify", &notify);
  add_rpc("get_finger_table_0", &get_finger_table_0);
  add_rpc("get_finger_table_3", &get_finger_table_3);

  add_rpc("create", &create);
  add_rpc("join", &join);
  add_rpc("find_successor", &find_successor);
}

void register_periodics() {
  add_periodic(check_predecessor);
  add_periodic(stablize);
  // add_periodic(fix_fingers);
}

#endif /* RPCS_H */
